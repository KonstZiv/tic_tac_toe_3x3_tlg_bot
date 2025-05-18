from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html, Dispatcher


# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # перевірити, чи є в базі даних юзер з таким id
    # якщо немає - додати юзера і спробу 1
    # якщо є - додати чергову спробу
    # Привітатись і коротке пояснення

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """

    await message.answer("Nice try!")
