"""Client module"""

from yandex_music import Client, ClientAsync

from utils.settings import settings



async def get_client():
    client: ClientAsync = await ClientAsync(token=settings.token).init()
    return client