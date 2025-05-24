from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_NAME: str
    BOT_USERNAME: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = Field(..., alias="POSTGRES_HOST_CONTAINER")
    POSTGRES_PORT: int = Field(..., alias="POSTGRES_PORT_CONTAINER")

    # Django API
    DJANGO_HOST: str
    DJANGO_PORT: int

    @property
    def db_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


    @property
    def api_url(self):
        return f"http://host.docker.internal:{self.DJANGO_PORT}/api/v1/"


settings = Settings()
