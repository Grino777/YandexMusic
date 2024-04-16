"""Settings module"""

from pydantic import BaseModel
from config import TOKEN, clients_uid


class Settings(BaseModel):
    """Settings class"""

    token: str = TOKEN
    clients_uid: dict = clients_uid


settings = Settings()
