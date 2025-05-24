from aiogram.types import User
from pydantic import BaseModel, Field


class UserShema(BaseModel):
    id: int | None = Field(default=None, description="User ID", gt=0)
    tg_id: int = Field(..., description="User ID", gt=0)
    tg_first_name: str = Field(..., description="User first name", max_length=255)
    tg_last_name: str | None = Field(default=None, description="User last name", max_length=255)
    tg_username: str | None = Field(default=None, description="User username", max_length=255)
    is_bot: bool = Field(default=False, description="Is user a bot")
    language_code: str | None = Field(default=None, description="User language code", max_length=10)
    is_premium: bool | None = Field(default=None, description="Is user a premium user")
    added_to_attachment_menu: bool | None = Field(default=None, description="Is user added to attachment menu")
    is_active: bool = Field(default=True, description="Is user active")

    @classmethod
    def user_from_dict(cls, user_dict: dict) -> "UserShema":
        """
        Create a User instance from a dictionary.
        """
        return cls(
            id=user_dict.get("id"),
            tg_id=user_dict.get("id"),
            tg_first_name=user_dict.get("first_name"),
            tg_last_name=user_dict.get("last_name"),
            tg_username=user_dict.get("username"),
            is_bot=user_dict.get("is_bot", False),
            language_code=user_dict.get("language_code"),
            is_premium=user_dict.get("is_premium", False),
            added_to_attachment_menu=user_dict.get("added_to_attachment_menu", False),
            is_active=True,
        )

    @classmethod
    def user_from_aiogram(cls, user: User) -> "UserShema":
        """
        Create a User instance from an aiogram User object.
        """
        return cls(
            id=None,  # ID will be set by the database
            tg_id=user.id,
            tg_first_name=user.first_name,
            tg_last_name=user.last_name,
            tg_username=user.username,
            is_bot=user.is_bot,
            language_code=user.language_code,
            is_premium=user.is_premium,
            added_to_attachment_menu=user.added_to_attachment_menu,
            is_active=True,
        )
