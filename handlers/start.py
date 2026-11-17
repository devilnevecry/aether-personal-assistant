"""Start command, main menu and common navigation handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import Database
from keyboards.inline import (
    finance_menu_keyboard,
    notes_menu_keyboard,
    tasks_menu_keyboard,
)
from keyboards.reply import main_menu_keyboard

router = Router()


HELP_TEXT = (
    "Я персональный помощник.\n\n"
    "📋 Задачи: добавляйте задачи с дедлайном, смотрите активные и отмечайте выполненные.\n"
    "📝 Заметки: сохраняйте текст с тегом и ищите по тегу.\n"
    "💰 Финансы: записывайте расходы и смотрите сводку за текущий месяц.\n\n"
    "Используйте меню ниже для навигации."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database) -> None:
    """Register the user and show the main menu."""
    await state.clear()
    await db.add_user(message.from_user.id)
    await message.answer(
        "Привет! Я ваш персональный помощник.\nВыберите раздел в меню ниже.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(lambda message: message.text == "📋 Задачи")
async def open_tasks_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Управление задачами:", reply_markup=tasks_menu_keyboard())


@router.message(lambda message: message.text == "📝 Заметки")
async def open_notes_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Управление заметками:", reply_markup=notes_menu_keyboard())


@router.message(lambda message: message.text == "💰 Финансы")
async def open_finance_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Учет финансов:", reply_markup=finance_menu_keyboard())


@router.message(lambda message: message.text == "❓ Помощь")
async def open_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(lambda call: call.data == "menu:tasks")
async def tasks_menu_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if call.message:
        await call.message.edit_text("Управление задачами:", reply_markup=tasks_menu_keyboard())
    await call.answer()


@router.callback_query(lambda call: call.data == "menu:notes")
async def notes_menu_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if call.message:
        await call.message.edit_text("Управление заметками:", reply_markup=notes_menu_keyboard())
    await call.answer()


@router.callback_query(lambda call: call.data == "menu:finance")
async def finance_menu_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if call.message:
        await call.message.edit_text("Учет финансов:", reply_markup=finance_menu_keyboard())
    await call.answer()


@router.callback_query(lambda call: call.data == "menu:main")
async def main_menu_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if call.message:
        await call.message.edit_text("Главное меню:", reply_markup=None)
        await call.message.answer("Выберите раздел в меню ниже.", reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(lambda call: call.data == "cancel")
async def cancel_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if call.message:
        await call.message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
    await call.answer()
