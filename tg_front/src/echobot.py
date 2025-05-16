from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html, Dispatcher

from tg_front.db.execute import execute_query
from tg_front.settings import settings

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    timestamp_now = datetime.now(tz=ZoneInfo("UTC")).isoformat(sep=" ")
    print(f"{message.from_user.id=}, {message.from_user.full_name=},")
    print(f"{message.chat.id=}, {message.chat.title=}, {message.chat.type=}")

    insert_query = f"""
        INSERT INTO message (text, user_id, created_at)
        VALUES ('{message.text}', {message.from_user.id}, '{timestamp_now}');
        """
    execute_query(settings=settings, query=insert_query)

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    print(f"{message.from_user.id=}, {message.from_user.full_name=},")
    print(f"{message.chat.id=}, {message.chat.title=}, {message.chat.type=}")
    try:
        timestamp_now = datetime.now(tz=ZoneInfo("UTC")).isoformat(sep=" ")
        insert_query = f"""
                INSERT INTO message (text, user_id, created_at)
                VALUES ('{message.text}', {message.from_user.id}, '{timestamp_now}');
                """
        execute_query(settings=settings, query=insert_query)
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")
