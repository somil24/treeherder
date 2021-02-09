import logging

from typing import List

from treeherder.perf.email import EmailWriter, FXPERF_TEST_ENG_EMAIL
from treeherder.perf.models import PerformanceSignature

logger = logging.getLogger(__name__)


class DeleteReportContent:
    DESCRIPTION = """Perfherder removes performance data that is older than one year and in some cases even sooner, leaving behind performance signatures that aren't associated to any data point. These as well need to be removed.
    > __Here's a summary of recently deleted performance signatures:__
    ---
        """

    TABLE_HEADERS = """
    | Repository | Framework | Platform | Suite | Application |
    | :---: | :---: | :---: | :---: | :---: |
        """

    def __init__(self):
        self._raw_content = None

    def include_signatures(self, signatures: List[PerformanceSignature]):
        self._initialize_report_intro()

        for signature in signatures:
            self._include_in_report(signature)

    def _initialize_report_intro(self):
        if self._raw_content is None:
            self._raw_content = self.DESCRIPTION + self.TABLE_HEADERS

    def _include_in_report(self, signature: PerformanceSignature):
        new_table_row = self._build_table_row(signature)
        self._raw_content += f"{new_table_row}\n"

    def _build_table_row(self, signature: PerformanceSignature) -> str:
        props = self.__extract_properties(signature)

        return '| {repository} | {framework} | {platform} | {suite} | {application} |'.format(
            repository=props["repository"],
            framework=props["framework"],
            platform=props["platform"],
            suite=props["suite"],
            application=props["application"],
        )

    def __extract_properties(self, signature: PerformanceSignature) -> dict:
        return {
            "repository": signature.repository.name,
            "framework": signature.framework.name,
            "platform": signature.platform.platform,
            "suite": signature.suite,
            "application": signature.application,
        }

    def __str__(self):
        if self._raw_content is None:
            # TODO: replace with proper exception type
            raise Exception("Programming error: content has not been set.")
        return self._raw_content


class DeleteNotificationWriter(EmailWriter):
    def _write_address(self):
        self._email.address = FXPERF_TEST_ENG_EMAIL

    def _write_subject(self):
        self._email.subject = "Summary of deleted Performance Signatures"

    def _write_content(self, must_mention: List[PerformanceSignature]):
        content = DeleteReportContent()
        content.include_signatures(must_mention)

        self._email.content = str(content)
