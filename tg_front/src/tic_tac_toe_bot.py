import logging

from aiogram import html, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from .api_requests import get_tguser, create_tguser
from .shemas import UserShema

logger = logging.getLogger(__name__)

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    user = UserShema.user_from_aiogram(message.from_user)
    logger.info(f"User data: {user} started the bot")
    # перевірити, чи є в базі даних юзер з таким id
    user_from_db = await get_tguser(user, message.bot)
    logger.info(f"User data from DB: {user_from_db}")
    if user_from_db:
        # якщо є - перевірити, чи активний
        # якщо активний - додати чергову спробу
        # якщо не активний - активувати юзера і додати чергову спробу
        pass
    else:
        # якщо немає - додати юзера і спробу 1
        pass
    # Привітатись і коротке пояснення

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    user = UserShema.user_from_aiogram(message.from_user)
    logger.info(f"User data: {user} started the bot")
    # перевірити, чи є в базі даних юзер з таким id
    user_db = await create_tguser(user, message.bot)

    await message.answer(f"Nice try! user added/updated to DB: {user_db}")
