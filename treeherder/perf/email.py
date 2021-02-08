from copy import copy

from typing import List

from treeherder.perf.models import BackfillRecord


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


class BackfillNotification:
    SUBJECT_TEMPLATE = 'Backfill hourly report'

    def __init__(self):
        self._address = None
        self._content: ReportContent = None
        self._subject = copy(self.SUBJECT_TEMPLATE)

    @property
    def address(self):
        if self._address is None:
            # TODO: replace with proper exception type
            raise Exception("Programming error: recipient address has not been set.")
        return self._address

    @address.setter
    def address(self, address: str):
        self._address = address

    @property
    def content(self):
        if self._content is None:
            # TODO: replace with proper exception type
            raise Exception("Programming error: content has not been set.")
        return str(self._content)

    @property
    def subject(self):
        return self._subject

    def include_records(self, records: List[BackfillRecord]):
        self._content = ReportContent()
        self._content.include_records(records)

    def as_payload(self) -> dict:
        return {
            "address": self.address,
            "content": self.content,
            "subject": self.subject,
        }
