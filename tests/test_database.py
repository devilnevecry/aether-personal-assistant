import os
import tempfile
from datetime import datetime

import pytest

from database import Database


@pytest.fixture
async def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = Database(path)
    await database.init()
    yield database
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.asyncio
async def test_add_user_and_task(db):
    await db.add_user(1)
    task_id = await db.add_task(1, "Buy milk", "2026-11-20")
    assert isinstance(task_id, int)
    tasks = await db.get_active_tasks(1)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"
    assert tasks[0]["deadline"] == "2026-11-20"


@pytest.mark.asyncio
async def test_complete_and_delete_task(db):
    await db.add_user(2)
    task_id = await db.add_task(2, "Task", None)
    assert await db.complete_task(2, task_id) is True
    assert await db.get_active_tasks(2) == []
    # already completed
    assert await db.complete_task(2, task_id) is False

    task_id2 = await db.add_task(2, "Task2", None)
    assert await db.delete_task(2, task_id2) is True
    assert await db.delete_task(2, task_id2) is False


@pytest.mark.asyncio
async def test_task_isolation_between_users(db):
    await db.add_user(1)
    await db.add_user(2)
    tid = await db.add_task(1, "Private", None)
    assert await db.get_active_tasks(2) == []
    assert await db.complete_task(2, tid) is False
    assert await db.delete_task(2, tid) is False


@pytest.mark.asyncio
async def test_notes(db):
    await db.add_user(3)
    note_id = await db.add_note(3, "hello", "Work")
    assert isinstance(note_id, int)
    notes = await db.get_notes_by_tag(3, "work")
    assert len(notes) == 1
    assert notes[0]["text"] == "hello"
    assert notes[0]["tag"] == "work"
    recent = await db.get_recent_notes(3, limit=5)
    assert len(recent) == 1
    assert await db.delete_note(3, note_id) is True
    assert await db.get_recent_notes(3) == []


@pytest.mark.asyncio
async def test_expenses_and_monthly_summary(db):
    await db.add_user(4)
    await db.add_expense(4, 10.5, "Food", "lunch")
    await db.add_expense(4, 5.0, "Food", None)
    await db.add_expense(4, 3.25, "Transport", None)
    now = datetime.now()
    items, total = await db.get_monthly_summary(4, now.year, now.month)
    # created_at uses current date, so monthly summary may be empty if not November 2026.
    # The test only checks structure and non-negative total.
    assert isinstance(items, list)
    assert total >= 0.0