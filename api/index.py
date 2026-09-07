import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from bot import BOT_TOKEN, router

logging.basicConfig(level=logging.INFO)

dispatcher = Dispatcher()
dispatcher.include_router(router)


async def process_update(payload: dict) -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN Vercel Environment Variables ichida sozlanmagan")

    bot = Bot(token=BOT_TOKEN)
    try:
        await dispatcher.feed_update(bot, Update.model_validate(payload))
    finally:
        with suppress(Exception):
            await bot.session.close()


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            asyncio.run(process_update(payload))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            logging.exception("Telegram webhook update qayta ishlanmadi")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Webhook processing failed")

    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"EduNova bot webhook is running")