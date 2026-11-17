"""Inline keyboard layouts."""

from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def tasks_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="task:add")],
            [InlineKeyboardButton(text="📄 Активные задачи", callback_data="task:list")],
            [InlineKeyboardButton(text="↩️ В главное меню", callback_data="menu:main")],
        ]
    )


def task_actions_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task:done:{task_id}"),
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"task:del:{task_id}"),
            ]
        ]
    )


def notes_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить заметку", callback_data="note:add")],
            [InlineKeyboardButton(text="🔎 Поиск по тегу", callback_data="note:search")],
            [InlineKeyboardButton(text="📄 Все заметки", callback_data="note:list")],
            [InlineKeyboardButton(text="↩️ В главное меню", callback_data="menu:main")],
        ]
    )


def note_actions_keyboard(note_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"note:del:{note_id}")]
        ]
    )


def finance_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить расход", callback_data="finance:add")],
            [InlineKeyboardButton(text="📊 Сводка за месяц", callback_data="finance:summary")],
            [InlineKeyboardButton(text="↩️ В главное меню", callback_data="menu:main")],
        ]
    )


def category_keyboard() -> InlineKeyboardMarkup:
    categories = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье", "Другое"]
    rows = [[InlineKeyboardButton(text=category, callback_data=f"finance:cat:{category}")] for category in categories]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tasks_group_keyboard(tasks: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    rows = []
    for task in tasks:
        task_id = task["id"]
        rows.append(
            [
                InlineKeyboardButton(text=f"✅ #{task_id}", callback_data=f"task:done:{task_id}"),
                InlineKeyboardButton(text=f"🗑 #{task_id}", callback_data=f"task:del:{task_id}"),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def notes_group_keyboard(notes: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"🗑 #{note['id']}", callback_data=f"note:del:{note['id']}")] for note in notes]
    return InlineKeyboardMarkup(inline_keyboard=rows)
