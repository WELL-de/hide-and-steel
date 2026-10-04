import asyncio
import logging
import subprocess

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

BOT_TOKEN = "8999414099:AAHU__7FmaUwavacTsq9R31iHVxCN9SBB1k"

# Вставь сюда СВОЙ telegram user id (узнать у @userinfobot)
ALLOWED_USER_ID = 7401276862

# --- ПРОКСИ ---
# Формат: "socks5://ЛОГИН:ПАРОЛЬ@IP:ПОРТ"
# Если прокси без авторизации: "socks5://IP:ПОРТ"
# Если HTTP-прокси: "http://ЛОГИН:ПАРОЛЬ@IP:ПОРТ"
PROXY_URL = "socks5://tu2oB3:kMKaNw@45.153.218.172:8000"
# --------------

logging.basicConfig(level=logging.INFO)

# Создаём сессию с прокси
session = AiohttpSession(proxy=PROXY_URL)

bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()


def is_allowed(message: Message) -> bool:
    return message.from_user and message.from_user.id == ALLOWED_USER_ID


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if not is_allowed(message):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer(
        "Готов. Пиши команду, я выполню её и пришлю вывод.\n"
        "Пример: `dir` или `ipconfig`"
    )


@dp.message(Command("sh"))
async def cmd_sh(message: Message, command: CommandObject):
    if not is_allowed(message):
        await message.answer("⛔ Нет доступа.")
        return
    if not command.args:
        await message.answer("Использование: /sh <команда>")
        return
    await run_and_reply(message, command.args)


@dp.message(F.text)
async def run_any(message: Message):
    if not is_allowed(message):
        await message.answer("⛔ Нет доступа.")
        return
    await run_and_reply(message, message.text)


async def run_and_reply(message: Message, cmd: str):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout or ""
        err = result.stderr or ""
        text = (output + err).strip() or "(пусто)"
        if len(text) > 4000:
            text = text[:4000] + "\n... (обрезано)"
        await message.answer(f"```\n{text}\n```", parse_mode="Markdown")
    except subprocess.TimeoutExpired:
        await message.answer("⏱ Команда выполняется слишком долго (лимит 30 сек).")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())