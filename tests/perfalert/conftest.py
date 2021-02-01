from unittest.mock import MagicMock

import pytest

from treeherder.services.taskcluster import TaskclusterModel, TaskclusterModelImpl


@pytest.fixture
def job_from_try(eleven_job_blobs, create_jobs):
    job_blob = eleven_job_blobs[0]
    job = create_jobs([job_blob])[0]

    job.repository.is_try_repo = True
    job.repository.save()
    return job


@pytest.fixture
def taskcluster_mock() -> TaskclusterModel:
    return MagicMock(
        spec=TaskclusterModelImpl('https://fakerooturl.org', 'FAKE_CLIENT_ID', 'FAKE_ACCESS_TOKEN')
    )
