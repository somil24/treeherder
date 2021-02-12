import pytest

from treeherder.perf.email import DeleteNotificationWriter, DeleteReportContent


class TestDeleteReportContent:
    def test_error_out_when_trying_to_serialize_empty_content(self):
        content = DeleteReportContent()

        with pytest.raises(ValueError, match="No content set"):
            _ = str(content)


class TestDeleteNotificationWriter:
    def test_writing_content_without_mentioning_any_signature_doesnt_error_out(self):
        email_writer = DeleteNotificationWriter()

        try:
            email_writer.prepare_new_email([])
        except ValueError as ex:
            if str(ex) == "No content set":
                pytest.fail(
                    "DeleteNotificationWriter must be able to provide a default content, "
                    "even if there's nothing to mention."
                )
            raise ex
