import logging

from treeherder.perf.models import PerformanceSignature

logger = logging.getLogger(__name__)


class EmailService:
    """
    This class handles the payload format required for emails
     sent through the `PublicSignatureRemover`.
    """

    TABLE_DESCRIPTION = """Perfherder removes performance data that is older than one year and in some cases even sooner, leaving behind performance signatures that aren't associated to any data point. These as well need to be removed.
> __Here's a summary of recently deleted performance signatures:__
---
    """

    TABLE_HEADERS = """
| Repository | Framework | Platform | Suite | Application |
| :---: | :---: | :---: | :---: | :---: |
    """

    def __init__(self, address: str, content=None):
        self._subject = "Summary of deleted Performance Signatures"
        self._content = content
        self._address = address

    @property
    def address(self):
        return self._address

    @property
    def subject(self):
        return self._subject

    @property
    def content(self):
        if self._content is None:
            self._content = self.TABLE_DESCRIPTION + self.TABLE_HEADERS
        return self._content

    @content.setter
    def content(self, content: str):
        self._content = content

    def add_signature_to_content(self, signature: PerformanceSignature):
        if signature:
            signature_properties = self._extract_properties(signature)
            signature_row = (
                """| {repository} | {framework} | {platform} | {suite} | {application} |""".format(
                    repository=signature_properties["repository"],
                    framework=signature_properties["framework"],
                    platform=signature_properties["platform"],
                    suite=signature_properties["suite"],
                    application=signature_properties["application"],
                )
            )
            self._content = self.content + signature_row
            self._content += "\n"
        else:
            self._content = None

    @property
    def payload(self) -> dict:
        return {
            "address": self.address,
            "content": self.content,
            "subject": self.subject,
        }

    def _extract_properties(self, signature: PerformanceSignature) -> dict:
        return {
            "repository": signature.repository.name,
            "framework": signature.framework.name,
            "platform": signature.platform.platform,
            "suite": signature.suite,
            "application": signature.application,
        }


# class ReportContent:
#     DESCRIPTION = """Perfherder removes performance data that is older than one year and in some cases even sooner, leaving behind performance signatures that aren't associated to any data point. These as well need to be removed.
#     > __Here's a summary of recently deleted performance signatures:__
#     ---
#         """
#
#     TABLE_HEADERS = """
#     | Repository | Framework | Platform | Suite | Application |
#     | :---: | :---: | :---: | :---: | :---: |
#         """
#
#     def __init__(self):
#         self._raw_content = None
#
#     def include_signatures(self, signatures: List[PerformanceSignature]):
#         self._initialize_report_intro()
#
#         for signature in signatures:
#             self._include_in_report(signature)
#
#     def _initialize_report_intro(self):
#         if self._raw_content is None:
#             self._raw_content = self.DESCRIPTION + self.TABLE_HEADERS
#
#     def _include_in_report(self, signature: PerformanceSignature):
#         new_table_row = self._build_table_row(signature)
#         self._raw_content += f"{new_table_row}\n"
#
#     def _build_table_row(self, signature: PerformanceSignature) -> str:
#         p = self.__extract_properties(signature)
#
#         return f'| {p["repository"]} | {p["framework"]} | {platform} | {suite} | {application} |'
#
#     def __extract_properties(self, signature: PerformanceSignature) -> dict:
#         return {
#             "repository": signature.repository.name,
#             "framework": signature.framework.name,
#             "platform": signature.platform.platform,
#             "suite": signature.suite,
#             "application": signature.application,
#         }
#
#     # TODO: should I use __repr__() instead?
#
#     def __str__(self):
#         if self._raw_content is None:
#             # TODO: replace with proper exception type
#             raise Exception("Programming error: content has not been set.")
#         return self._raw_content
#
# class DeleteNotificationWriter(EmailWriter):
#     def _write_address(self):
#         self._email.address = RECEIVER_TEAM_EMAIL
#
#     def _write_subject(self):
#         self._email.subject = "Summary of deleted Performance Signatures"
#
#     def _write_content(self, must_mention: List[PerformanceSignature]):
#         self._content = ReportContent()
#         self._content.include_records(must_mention)
