import asyncio
import logging
import os
from contextlib import suppress

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", "7180980386")).split(",")
    if admin_id.strip()
]
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@edunova_maktabi")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/edunova_maktabi")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan")

logging.basicConfig(level=logging.INFO)
router = Router()


class FeedbackForm(StatesGroup):
    waiting_for_text = State()


def subscription_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga qo'shilish", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")],
        ]
    )


def main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💡 Taklif yuborish", callback_data="feedback:suggestion")
    builder.button(text="✉️ Murojaat yuborish", callback_data="feedback:appeal")
    builder.adjust(1)
    return builder.as_markup()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    except TelegramBadRequest:
        logging.exception("Kanal obunasini tekshirishda xatolik")
        return False

    return member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }


async def require_subscription(message: Message, bot: Bot) -> bool:
    if await is_subscribed(bot, message.from_user.id):
        return True

    await message.answer(
        "Botdan foydalanish uchun avval kanalimizga obuna bo'ling:",
        reply_markup=subscription_keyboard(),
    )
    return False


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.clear()
    if not await require_subscription(message, bot):
        return

    await message.answer(
        "Assalomu alaykum! Taklif yoki murojaatingizni yuborish uchun kerakli tugmani tanlang.",
        reply_markup=main_keyboard(),
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery, bot: Bot) -> None:
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.edit_text(
            "Obuna tasdiqlandi ✅\nEndi taklif yoki murojaatingizni yuborishingiz mumkin.",
            reply_markup=main_keyboard(),
        )
        await callback.answer("Obuna tasdiqlandi")
    else:
        await callback.answer("Avval kanalga obuna bo'ling", show_alert=True)


@router.callback_query(F.data.startswith("feedback:"))
async def feedback_type_handler(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    if not await is_subscribed(bot, callback.from_user.id):
        await callback.answer("Avval kanalga obuna bo'ling", show_alert=True)
        return

    feedback_type = callback.data.split(":", 1)[1]
    label = "taklif" if feedback_type == "suggestion" else "murojaat"
    await state.update_data(feedback_type=label)
    await state.set_state(FeedbackForm.waiting_for_text)
    await callback.message.answer(
        f"{label.capitalize()}ingizni bitta xabarda yozib yuboring. Bekor qilish uchun /cancel buyrug'ini yuboring."
    )
    await callback.answer()


@router.message(FeedbackForm.waiting_for_text, F.text != "/cancel")
async def feedback_message_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    if not await is_subscribed(bot, message.from_user.id):
        await state.clear()
        await require_subscription(message, bot)
        return

    data = await state.get_data()
    feedback_type = data.get("feedback_type", "murojaat")

    admin_text = (
        f"📩 Yangi {feedback_type}\n\n"
        f"{message.text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except TelegramBadRequest:
            logging.warning(
                "Admin %s ga xabar yuborilmadi. U botga /start yuborganini tekshiring.",
                admin_id,
            )
    await state.clear()
    await message.answer("Xabaringiz adminga yuborildi ✅", reply_markup=main_keyboard())


@router.message(FeedbackForm.waiting_for_text)
async def non_text_feedback_handler(message: Message) -> None:
    await message.answer("Iltimos, murojaat yoki taklifingizni matn ko'rinishida yuboring.")


@router.message(F.text == "/cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Yuborish bekor qilindi.", reply_markup=main_keyboard())


async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        with suppress(Exception):
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
