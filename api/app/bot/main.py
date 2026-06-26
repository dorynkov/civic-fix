"""Telegram bot stub (v1). Run: python -m app.bot.main"""

import asyncio
import os

from app.config import settings


async def main():
    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN not set — bot disabled")
        return
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command
    from aiogram.types import Message

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(msg: Message):
        await msg.answer("Civic Fix bot (v1). Open web app to report issues.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
