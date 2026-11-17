"""Finance tracking handlers."""

from __future__ import annotations

from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import Database
from keyboards.inline import category_keyboard, finance_menu_keyboard


router = Router()


class FinanceForm(StatesGroup):
    amount = State()
    category = State()
    comment = State()


@router.callback_query(F.data == "finance:add")
async def finance_add_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FinanceForm.amount)
    if call.message:
        await call.message.answer("Введите сумму расхода числом (например, 250.50):")
    await call.answer()


@router.message(FinanceForm.amount)
async def finance_amount_received(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip().replace(",", ".")
    try:
        amount = float(raw)
    except ValueError:
        await message.answer("Сумма должна быть числом. Попробуйте снова.")
        return

    if amount <= 0:
        await message.answer("Сумма должна быть больше нуля. Попробуйте снова.")
        return

    await state.update_data(amount=amount)
    await state.set_state(FinanceForm.category)
    await message.answer("Выберите категорию расхода:", reply_markup=category_keyboard())


@router.callback_query(F.data.startswith("finance:cat:"))
async def finance_category_received(call: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state != FinanceForm.category.state:
        await call.answer("Сначала начните добавление расхода.", show_alert=True)
        return

    category = (call.data or "").split(":", 2)[-1]
    if not category:
        await call.answer("Категория не выбрана.", show_alert=True)
        return

    await state.update_data(category=category)
    await state.set_state(FinanceForm.comment)
    if call.message:
        await call.message.answer("Введите комментарий или отправьте «нет»:")
    await call.answer()


@router.message(FinanceForm.comment)
async def finance_comment_received(message: Message, state: FSMContext, db: Database) -> None:
    raw = (message.text or "").strip()
    comment = None if raw.lower() in {"нет", "no", "-", "пропустить", "skip"} else raw

    data = await state.get_data()
    amount = data.get("amount")
    category = data.get("category")
    if amount is None or not category:
        await state.clear()
        await message.answer("Не хватает данных для расхода. Начните добавление заново.")
        return

    expense_id = await db.add_expense(message.from_user.id, float(amount), category, comment)
    await state.clear()
    comment_text = comment or "без комментария"
    await message.answer(
        f"💸 Расход #{expense_id} записан.\n"
        f"Сумма: {amount:.2f}\n"
        f"Категория: {category}\n"
        f"Комментарий: {comment_text}"
    )


@router.callback_query(F.data == "finance:summary")
async def finance_summary(call: CallbackQuery, db: Database) -> None:
    now = datetime.now()
    items, total = await db.get_monthly_summary(call.from_user.id, now.year, now.month)

    if not items:
        if call.message:
            await call.message.answer("За текущий месяц расходов пока нет.")
        await call.answer()
        return

    lines = [f"📊 Сводка за {now.month:02d}.{now.year}:", ""]
    for item in items:
        lines.append(f"{item['category']}: {item['total']:.2f}")
    lines.append("")
    lines.append(f"Итого: {total:.2f}")

    if call.message:
        await call.message.answer("\n".join(lines))
    await call.answer()
