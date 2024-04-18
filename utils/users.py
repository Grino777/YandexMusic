from config import CLIENTS
from pydantic import BaseModel

clients = CLIENTS

class YandexUser(BaseModel):
    id: int
    name: str
    uid: int

yandex_clients = [YandexUser(**client) for client in clients]