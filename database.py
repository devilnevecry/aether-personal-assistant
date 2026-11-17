"""SQLite database helpers for the personal assistant bot."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

import aiosqlite


class Database:
    """Small async wrapper around an SQLite database."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def init(self) -> None:
        """Create all required tables if they do not exist yet."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    deadline TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );

                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    comment TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );
                """
            )
            await db.commit()

    async def add_user(self, user_id: int) -> None:
        """Register a user without duplicating an existing record."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)",
                (user_id, datetime.now().isoformat()),
            )
            await db.commit()

    async def add_task(self, user_id: int, title: str, deadline: str | None) -> int:
        """Insert a task and return its id."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO tasks (user_id, title, deadline, status, created_at)
                VALUES (?, ?, ?, 'active', ?)
                """,
                (user_id, title, deadline, datetime.now().isoformat()),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def get_active_tasks(self, user_id: int) -> list[dict[str, Any]]:
        """Return all active tasks for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, title, deadline, created_at
                FROM tasks
                WHERE user_id = ? AND status = 'active'
                ORDER BY id DESC
                """,
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def complete_task(self, user_id: int, task_id: int) -> bool:
        """Mark an active task as completed. Returns True when a row was changed."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                UPDATE tasks
                SET status = 'done'
                WHERE id = ? AND user_id = ? AND status = 'active'
                """,
                (task_id, user_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def delete_task(self, user_id: int, task_id: int) -> bool:
        """Delete a task owned by the user."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def add_note(self, user_id: int, text: str, tag: str) -> int:
        """Insert a note and return its id."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO notes (user_id, text, tag, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, text, tag.lower(), datetime.now().isoformat()),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def get_notes_by_tag(self, user_id: int, tag: str) -> list[dict[str, Any]]:
        """Return notes whose tag matches the requested tag."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, text, tag, created_at
                FROM notes
                WHERE user_id = ? AND tag = ?
                ORDER BY id DESC
                """,
                (user_id, tag.lower()),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_recent_notes(self, user_id: int, limit: int = 20) -> list[dict[str, Any]]:
        """Return recently created notes."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, text, tag, created_at
                FROM notes
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_note(self, user_id: int, note_id: int) -> bool:
        """Delete a note owned by the user."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM notes WHERE id = ? AND user_id = ?",
                (note_id, user_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def add_expense(
        self,
        user_id: int,
        amount: float,
        category: str,
        comment: str | None,
    ) -> int:
        """Insert an expense and return its id."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO expenses (user_id, amount, category, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, category, comment, datetime.now().isoformat()),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def get_monthly_summary(
        self,
        user_id: int,
        year: int,
        month: int,
    ) -> tuple[list[dict[str, Any]], float]:
        """Return expense totals grouped by category for one month."""
        month_prefix = f"{year:04d}-{month:02d}-"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT category, SUM(amount) AS total
                FROM expenses
                WHERE user_id = ? AND created_at LIKE ?
                GROUP BY category
                ORDER BY total DESC
                """,
                (user_id, f"{month_prefix}%"),
            )
            rows = await cursor.fetchall()
            items = [{"category": row["category"], "total": float(row["total"])} for row in rows]
            grand_total = sum(item["total"] for item in items)
            return items, grand_total
