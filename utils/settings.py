"""Settings module"""

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

ENV = load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    """Settings class"""

    token: str


settings = Settings()
