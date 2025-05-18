import aiohttp
from aiogram import Bot


async def add_aiohttp_client_session(bot: Bot):
    # Створюємо сесію aiohttp під час запуску бота
    bot['http_session'] = aiohttp.ClientSession()
    print("Aiohttp client session created.")


async def close_aiohttp_client_session(bot: Bot):
    # Закриваємо сесію aiohttp під час завершення роботи бота
    if "http_session" in bot:
        await bot['http_session'].close()
    print("Aiohttp client session closed.")
