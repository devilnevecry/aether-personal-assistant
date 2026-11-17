from handlers.tasks import _parse_task_id


def test_parse_task_id_valid():
    assert _parse_task_id("task:done:42") == 42
    assert _parse_task_id("task:del:7") == 7


def test_parse_task_id_invalid():
    assert _parse_task_id("task:done:abc") is None
    assert _parse_task_id("") is None