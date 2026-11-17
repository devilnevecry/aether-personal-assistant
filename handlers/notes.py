"""Quick notes handlers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import Database
from keyboards.inline import notes_group_keyboard

router = Router()


class NoteForm(StatesGroup):
    text = State()
    tag = State()
    search_tag = State()


def _parse_note_id(callback_data: str) -> int | None:
    try:
        return int(callback_data.rsplit(":", 1)[-1])
    except (ValueError, IndexError):
        return None


@router.callback_query(F.data == "note:add")
async def note_add_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NoteForm.text)
    if call.message:
        await call.message.answer("Введите текст заметки:")
    await call.answer()


@router.message(NoteForm.text)
async def note_text_received(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Текст заметки не может быть пустым. Попробуйте снова.")
        return
    await state.update_data(text=text)
    await state.set_state(NoteForm.tag)
    await message.answer("Введите тег для заметки (например, #работа или работа):")


@router.message(NoteForm.tag)
async def note_tag_received(message: Message, state: FSMContext, db: Database) -> None:
    tag = (message.text or "").strip().lstrip("#").strip()
    if not tag:
        await message.answer("Тег не может быть пустым. Попробуйте снова.")
        return

    data = await state.get_data()
    text = data.get("text")
    if not text:
        await state.clear()
        await message.answer("Не найден текст заметки. Начните добавление заново.")
        return

    note_id = await db.add_note(message.from_user.id, text, tag)
    await state.clear()
    await message.answer(f"📝 Заметка #{note_id} сохранена с тегом #{tag}.")


@router.callback_query(F.data == "note:search")
async def note_search_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NoteForm.search_tag)
    if call.message:
        await call.message.answer("Введите тег для поиска:")
    await call.answer()


@router.message(NoteForm.search_tag)
async def note_search_tag_received(message: Message, state: FSMContext, db: Database) -> None:
    tag = (message.text or "").strip().lstrip("#").strip()
    if not tag:
        await message.answer("Тег не может быть пустым.")
        return

    notes = await db.get_notes_by_tag(message.from_user.id, tag)
    await state.clear()
    if not notes:
        await message.answer(f"Заметок с тегом #{tag} не найдено.")
        return

    for chunk_index in range(0, len(notes), 10):
        chunk = notes[chunk_index : chunk_index + 10]
        part = ""
        if len(notes) > 10:
            part = f" (часть {chunk_index // 10 + 1})"
        lines = [f"🔎 Заметки по тегу #{tag}: всего {len(notes)}{part}", ""]
        lines.extend(f"#{note['id']} {note['text']}" for note in chunk)
        await message.answer(
            "\n".join(lines),
            reply_markup=notes_group_keyboard(chunk),
        )


@router.callback_query(F.data == "note:list")
async def note_list(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    notes = await db.get_recent_notes(call.from_user.id, limit=200)
    if not notes:
        if call.message:
            await call.message.answer("Заметок пока нет.")
        await call.answer()
        return

    if not call.message:
        await call.answer()
        return

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note in notes:
        groups[note["tag"]].append(note)

    for tag in sorted(groups):
        group_notes = groups[tag]
        for chunk_index in range(0, len(group_notes), 10):
            chunk = group_notes[chunk_index : chunk_index + 10]
            part = ""
            if len(group_notes) > 10:
                part = f" (часть {chunk_index // 10 + 1})"
            lines = [f"📝 Заметки с тегом #{tag}{part}", ""]
            lines.extend(f"#{note['id']} {note['text']}" for note in chunk)
            await call.message.answer(
                "\n".join(lines),
                reply_markup=notes_group_keyboard(chunk),
            )

    await call.answer()


@router.callback_query(F.data.startswith("note:del:"))
async def note_delete(call: CallbackQuery, db: Database) -> None:
    note_id = _parse_note_id(call.data or "")
    if note_id is None:
        await call.answer("Некорректный идентификатор заметки.", show_alert=True)
        return

    deleted = await db.delete_note(call.from_user.id, note_id)
    if deleted:
        await call.answer("Заметка удалена.")
        if call.message:
            await call.message.edit_text(f"🗑 Заметка #{note_id} удалена.")
    else:
        await call.answer("Заметка не найдена.", show_alert=True)
