import aiohttp
from aiogram import Bot
import logging

logger = logging.getLogger(__name__)


async def add_aiohttp_client_session(bot: Bot):
    # Створюємо сесію aiohttp під час запуску бота
    bot.http_session = aiohttp.ClientSession()
    logger.info("Aiohttp client session created.")


async def close_aiohttp_client_session(bot: Bot):
    # Закриваємо сесію aiohttp під час завершення роботи бота
    if hasattr(bot, 'http_session'):
        await bot.http_session.close()
    logger.info("Aiohttp client session closed.")


async def make_api_request(url, bot: Bot):
    # Використовуємо збережену сесію для запитів
    if not hasattr(bot, 'http_session'):
        raise RuntimeError("HTTP session not initialized. Please call add_aiohttp_client_session first.")
    session = bot.http_session
    async with session.get(url) as response:
        return await response.json()
