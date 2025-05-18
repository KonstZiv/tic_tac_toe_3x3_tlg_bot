import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from settings import settings
from src.tic_tac_toe_bot import dp

from src.utils import add_aiohttp_client_session, close_aiohttp_client_session

# Bot token can be obtained via https://t.me/BotFather
TOKEN = settings.BOT_TOKEN
dp.startup.register(add_aiohttp_client_session)
dp.shutdown.register(close_aiohttp_client_session)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
