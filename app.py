import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from flask import Flask, request

from bot import BOT_TOKEN, router

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
dispatcher = Dispatcher()
dispatcher.include_router(router)


async def process_update(payload: dict) -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable ichida sozlanmagan")

    bot = Bot(token=BOT_TOKEN)
    try:
        await dispatcher.feed_update(bot, Update.model_validate(payload))
    finally:
        with suppress(Exception):
            await bot.session.close()


@app.get("/")
def healthcheck():
    return "EduNova bot is running", 200


@app.post("/webhook")
def webhook():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return "Invalid Telegram update", 400

    try:
        asyncio.run(process_update(payload))
    except Exception:
        logging.exception("Telegram webhook update qayta ishlanmadi")
        return "Webhook processing failed", 500

    return "OK", 200