from aiogram import Bot
from .shemas import UserShema
from settings import settings


async def get_tguser(
        user: UserShema,
        bot: Bot,
        api_url: str = settings.api_url,
) -> dict:
    url = f"{api_url}users/tgusers/{user.id}/?format=json"
    async with bot.http_session.get(url,) as response:
        return await response.json()


async def create_tguser(
        user: UserShema,
        bot: Bot,
        api_url: str = settings.api_url,
) -> dict:
    url = f"{api_url}users/tgusers/?format=json"
    async with bot.http_session.post(url, json=user.model_dump()) as response:
        result = await response.json()
        return result
