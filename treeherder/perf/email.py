from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from typing import List

from treeherder.perf.models import BackfillRecord

FXPERF_TEST_ENG_EMAIL = "perftest-alerts@mozilla.com"


@dataclass
class Email:
    address: str = None
    content: str = None
    subject: str = None

    def as_payload(self) -> dict:
        return asdict(self)


class ReportContent:
    DESCRIPTION = """Perfherder removes performance data that is older than one year and in some cases even sooner, leaving behind performance signatures that aren't associated to any data point. These as well need to be removed.
    > __Here's a summary of recently deleted performance signatures:__
    ---
        """

    TABLE_HEADERS = """
    | Alert summary | Alert | Job symbol | Total backfills (aprox.) | Push range |
    | :---: | :---: | :---: | :---: | :---: |
        """

    def __init__(self):
        self._raw_content = None

    def include_records(self, records: List[BackfillRecord]):
        self._initialize_report_intro()

        for record in records:
            self._include_in_report(record)

    def _initialize_report_intro(self):
        if self._raw_content is None:
            self._raw_content = self.DESCRIPTION + self.TABLE_HEADERS

    def _include_in_report(self, record: BackfillRecord):
        new_table_row = self._build_table_row(record)
        self._raw_content += f"{new_table_row}\n"

    def _build_table_row(self, record: BackfillRecord) -> str:
        alert_summary = record.alert.summary
        alert = record.alert
        job_type = record.job_type
        total_backfills = record.total_backfills_triggered
        # TODO: must add push range
        push_range = 'must add'

        # some fields require adjustments
        summary_id = alert_summary.id
        alert_id = alert.id
        job_symbol = str(job_type)

        return f"| {summary_id} | {alert_id} | {job_symbol} | {total_backfills} | {push_range} |"

    # TODO: should I use __repr__() instead?

    def __str__(self):
        if self._raw_content is None:
            # TODO: replace with proper exception type
            raise Exception("Programming error: content has not been set.")
        return self._raw_content


class EmailWriter(ABC):
    def __init__(self):
        self._email = Email()

    def prepare_email(self, must_mention: List[object]) -> dict:
        self._write_address()
        self._write_subject()
        self._write_content(must_mention)
        return self.email

    @property
    def email(self):
        return self._email.as_payload()

    @abstractmethod
    def _write_address(self):
        pass

    @abstractmethod
    def _write_subject(self):
        pass

    @abstractmethod
    def _write_content(self, must_mention: List[object]):
        pass


class BackfillNotificationWriter(EmailWriter):
    def _write_address(self):
        self._email.address = FXPERF_TEST_ENG_EMAIL

    def _write_subject(self):
        self._email.subject = "Backfill hourly report"

    def _write_content(self, must_mention: List[BackfillRecord]):
        self._content = ReportContent()
        self._content.include_records(must_mention)
