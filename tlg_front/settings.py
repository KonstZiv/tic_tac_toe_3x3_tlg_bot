import os


class Settings:
    def __init__(self):
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.BOT_NAME = os.environ.get("BOT_NAME")
        self.BOT_USERNAME = os.environ.get("BOT_USERNAME")

        # Database
        self.POSTGRES_USER = os.environ.get("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
        self.POSTGRES_DB = os.environ.get("POSTGRES_DB")
        self.POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
        self.POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT_HOST"))

    def __repr__(self):
        return f"Settings(BOT_TOKEN={self.BOT_TOKEN}, BOT_NAME={self.BOT_NAME}, BOT_USERNAME={self.BOT_USERNAME}, POSTGRES_USER={self.POSTGRES_USER}, POSTGRES_PASSWORD={self.POSTGRES_PASSWORD}, POSTGRES_DB={self.POSTGRES_DB}, POSTGRES_HOST={self.POSTGRES_HOST}, POSTGRES_PORT={self.POSTGRES_PORT})"

    @property
    def db_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
