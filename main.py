"""Download music app"""

import asyncio

from yandex_music import ClientAsync

from app.app import App
from downloader.downloader import YandexMusicDownloader
from utils.client import get_client


async def main():
    """Main def"""

    app = App()

    print(app._json_to_dict())

    # user = app.run_user_selection()

    # if user:
    #     client: ClientAsync = await get_client()

    #     downloader = YandexMusicDownloader(client=client, user=user, root_dir=root_dir)
    #     await downloader.init()
    # await app._get_the_favorite_playlist()

    print("DONE!")


if __name__ == "__main__":
    asyncio.run(main())
