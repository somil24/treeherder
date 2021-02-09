from datetime import datetime, timedelta
from json import JSONDecodeError

import pytest

from django.db import models

from treeherder.model.models import Job
from treeherder.perf.exceptions import MaxRuntimeExceeded
from treeherder.perf.models import BackfillRecord
from treeherder.perf.auto_perf_sheriffing.perf_sheriff_bot import PerfSheriffBot

EPOCH = datetime.utcfromtimestamp(0)


def has_changed(orm_object: models.Model) -> bool:
    """
    Checks if the ORM object's underlying table row
    has changed since last database sync.
    """
    db_obj = orm_object.__class__.objects.get(pk=orm_object.pk)
    for f in orm_object._meta.local_fields:
        if orm_object.__getattribute__(f.name) != db_obj.__getattribute__(f.name):
            return True
    return False


def test_assert_can_run_throws_exception_when_runtime_exceeded(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    record_ready_for_processing,
    sheriff_settings,
    notify_client_mock,
):
    no_time_left = timedelta(seconds=0)
    sheriff_settings = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, notify_client_mock, no_time_left
    )

    with pytest.raises(MaxRuntimeExceeded):
        sheriff_settings.assert_can_run()


def test_assert_can_run_doesnt_throw_exception_when_enough_time_left(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    record_ready_for_processing,
    sheriff_settings,
):
    enough_time_left = timedelta(minutes=10)
    sheriff_settings = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, enough_time_left
    )

    try:
        sheriff_settings.assert_can_run()
    except MaxRuntimeExceeded:
        pytest.fail()


def test_records_and_db_limits_remain_unchanged_if_no_records_suitable_for_backfill(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    notify_client_mock,
    sheriff_settings,
    record_unsuited_for_backfill,
):
    sheriff_bot = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, notify_client_mock
    )
    sheriff_bot._backfill()

    assert not has_changed(record_unsuited_for_backfill)
    assert not has_changed(sheriff_settings)


def test_records_remain_unchanged_if_no_backfills_left(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    notify_client_mock,
    record_ready_for_processing,
    empty_sheriff_settings,
):
    sheriff_bot = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, notify_client_mock
    )
    sheriff_bot._backfill()

    assert not has_changed(record_ready_for_processing)


# @pytest.mark.xfail(reason="TODO: fix test; probably requires some refactoring")
def test_records_and_db_limits_remain_unchanged_if_runtime_exceeded(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    record_ready_for_processing,
    sheriff_settings,
    notify_client_mock,
):
    no_time_left = timedelta(seconds=0)
    sheriff_bot = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, notify_client_mock, no_time_left
    )
    try:
        sheriff_bot.sheriff(since=EPOCH, frameworks=['raptor', 'talos'], repositories=['autoland'])
    except MaxRuntimeExceeded:
        pass

    assert not has_changed(record_ready_for_processing)
    assert not has_changed(sheriff_settings)


@pytest.mark.xfail(reason="TODO: fix test; probably requires some refactoring")
def test_db_limits_update_if_backfills_left(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    record_ready_for_processing,
    sheriff_settings,
):
    initial_backfills = secretary.backfills_left(on_platform='linux')
    sheriff_bot = PerfSheriffBot(report_maintainer_mock, backfill_tool_mock, secretary)
    sheriff_bot._backfill()

    record_ready_for_processing.refresh_from_db()
    assert record_ready_for_processing.status == BackfillRecord.BACKFILLED
    assert (initial_backfills - 5) == secretary.backfills_left(on_platform='linux')


def test_backfilling_gracefully_handles_invalid_json_contexts_without_blowing_up(
    report_maintainer_mock,
    backfill_tool_mock,
    secretary,
    record_ready_for_processing,
    sheriff_settings,
    notify_client_mock,
    broken_context_str,  # Note: parametrizes the test
):
    record_ready_for_processing.context = broken_context_str
    record_ready_for_processing.save()

    sheriff_bot = PerfSheriffBot(
        report_maintainer_mock, backfill_tool_mock, secretary, notify_client_mock
    )
    try:
        sheriff_bot.sheriff(since=EPOCH, frameworks=['raptor', 'talos'], repositories=['autoland'])
    except (JSONDecodeError, KeyError, Job.DoesNotExist):
        pytest.fail()

    record_ready_for_processing.refresh_from_db()

    assert record_ready_for_processing.status == BackfillRecord.FAILED
    assert not has_changed(sheriff_settings)
