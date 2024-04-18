"""Client module"""

from yandex_music import ClientAsync
from config import TOKEN


async def get_client():
    """Get session"""
    client: ClientAsync = await ClientAsync(token=TOKEN).init()
    return client
