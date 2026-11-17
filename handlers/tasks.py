"""Task (to-do) handlers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import Database
from keyboards.inline import task_actions_keyboard, tasks_group_keyboard, tasks_menu_keyboard


router = Router()


class TaskForm(StatesGroup):
    title = State()
    deadline = State()


def _parse_task_id(callback_data: str) -> int | None:
    try:
        return int(callback_data.rsplit(":", 1)[-1])
    except (ValueError, IndexError):
        return None


@router.callback_query(F.data == "task:add")
async def task_add_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TaskForm.title)
    if call.message:
        await call.message.answer("Введите название задачи:")
    await call.answer()


@router.message(TaskForm.title)
async def task_title_received(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название задачи не может быть пустым. Попробуйте снова.")
        return
    await state.update_data(title=title)
    await state.set_state(TaskForm.deadline)
    await message.answer("Введите дедлайн в формате ГГГГ-ММ-ДД или отправьте «нет».")


@router.message(TaskForm.deadline)
async def task_deadline_received(message: Message, state: FSMContext, db: Database) -> None:
    raw = (message.text or "").strip()
    deadline: str | None = None

    if raw.lower() not in {"нет", "no", "-", "пропустить", "skip"}:
        try:
            datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД или отправьте «нет».")
            return
        deadline = raw

    data = await state.get_data()
    title = data.get("title")
    if not title:
        await state.clear()
        await message.answer("Не найдено название задачи. Начните добавление заново.")
        return

    task_id = await db.add_task(message.from_user.id, title, deadline)
    await state.clear()
    deadline_text = deadline or "не указан"
    await message.answer(
        f"✅ Задача #{task_id} добавлена.\nНазвание: {title}\nДедлайн: {deadline_text}"
    )


@router.callback_query(F.data == "task:list")
async def task_list(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    tasks = await db.get_active_tasks(call.from_user.id)
    if not tasks:
        if call.message:
            await call.message.answer("Активных задач нет.")
        await call.answer()
        return

    if not call.message:
        await call.answer()
        return

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        deadline = task["deadline"] or "Без дедлайна"
        groups[deadline].append(task)

    ordered_keys = sorted(key for key in groups if key != "Без дедлайна")
    if "Без дедлайна" in groups:
        ordered_keys.append("Без дедлайна")

    for deadline in ordered_keys:
        group_tasks = groups[deadline]
        for chunk_index in range(0, len(group_tasks), 10):
            chunk = group_tasks[chunk_index : chunk_index + 10]
            part = ""
            if len(group_tasks) > 10:
                part = f" (часть {chunk_index // 10 + 1})"
            lines = [f"📋 Активные задачи — дедлайн: {deadline}{part}", ""]
            lines.extend(f"#{task['id']} {task['title']}" for task in chunk)
            await call.message.answer(
                "\n".join(lines),
                reply_markup=tasks_group_keyboard(chunk),
            )

    await call.answer()


@router.callback_query(F.data.startswith("task:done:"))
async def task_done(call: CallbackQuery, db: Database) -> None:
    task_id = _parse_task_id(call.data or "")
    if task_id is None:
        await call.answer("Некорректный идентификатор задачи.", show_alert=True)
        return

    changed = await db.complete_task(call.from_user.id, task_id)
    if changed:
        await call.answer("Задача отмечена выполненной.")
        if call.message:
            await call.message.edit_text(f"✅ Задача #{task_id} выполнена.")
    else:
        await call.answer("Задача не найдена или уже выполнена.", show_alert=True)


@router.callback_query(F.data.startswith("task:del:"))
async def task_delete(call: CallbackQuery, db: Database) -> None:
    task_id = _parse_task_id(call.data or "")
    if task_id is None:
        await call.answer("Некорректный идентификатор задачи.", show_alert=True)
        return

    deleted = await db.delete_task(call.from_user.id, task_id)
    if deleted:
        await call.answer("Задача удалена.")
        if call.message:
            await call.message.edit_text(f"🗑 Задача #{task_id} удалена.")
    else:
        await call.answer("Задача не найдена.", show_alert=True)
