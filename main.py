"""Download music app"""

import asyncio
import os
from asyncio import Task
from typing import Dict, List, Union

from tqdm import tqdm
from transliterate import translit
from yandex_music import ClientAsync, Playlist, TrackShort
from yandex_music.track.track import Track

from utils.client import get_client


class YandexMusicDownloader:
    """Приложение для скачивания музыки"""

    ROOT_DIRECTORY = os.path.dirname((os.path.realpath(__file__)))
    NAME_MUSIC_FOLDER = "MUSIC"

    def __init__(self, client):
        self.client: ClientAsync = client
        self.user_playlists: List[Dict[str, Union[Playlist, str]]] = []

    def _get_split_list_of_tracks(self, tracks_list: List):
        """Функция для разбивки списка на подсписки по 5 треков"""
        chunk_size = 5

        for i in range(0, len(tracks_list), chunk_size):
            yield tracks_list[i : i + chunk_size]

    def _create_folders(self):
        """Создание папок по названию плейлистов"""

        for playlist_item in self.user_playlists:
            path = str(playlist_item.get("path"))
            if not os.path.exists(path):
                os.mkdir(path)

    async def _get_playlists_user(self):
        """Получить список плейлистов пользователя"""

        user_playlists = await self.client.users_playlists_list()

        if len(user_playlists) > 0:
            for playlist in user_playlists:
                old_title = str(playlist.title)
                title = old_title.replace("\xa0", " ")
                title = translit(title, language_code="ru", reversed=True)
                path = os.path.join(self.ROOT_DIRECTORY, self.NAME_MUSIC_FOLDER, title)

                self.user_playlists.append(
                    {"title": title, "playlist": playlist, "path": path}
                )
        else:
            print('У пользователя нет плейлисов либо они скрыты!')

    def _check_current_directory(self):
        """Проверка директории на наличие корневой папки music"""

        if not os.path.exists(self.NAME_MUSIC_FOLDER):
            os.makedirs(self.NAME_MUSIC_FOLDER)

    async def init(self):
        """Инициализация"""

        self._check_current_directory()
        await self._get_playlists_user()
        self._create_folders()

    async def download_tracks(self, track: Track, path: str = ""):
        """Загрузка трека"""

        try:
            filename = f"{track.artists[0].name} - {track.title}.mp3"
            track_path = str(os.path.join(path, filename))
            result = await track.download_async(
                filename=track_path, codec="mp3", bitrate_in_kbps=320
            )
            return result
        except Exception as e:
            print(e)

    async def get_tracks_from_playlists(self):
        """Получить треки из плейлистов"""

        for playlist_item in self.user_playlists:
            print(f"Скачивается плейлист: {playlist_item.get("title")}\n")

            tracks_list: List[TrackShort] = []

            path = playlist_item["path"]
            playlist: Playlist = playlist_item.get("playlist")  # type:ignore
            tracks_list.extend(await playlist.fetch_tracks_async())
            tracks: List[Track | None] = [item.track for item in tracks_list]

            new_tracks_list = list(self._get_split_list_of_tracks(tracks_list=tracks))

            for tracks_list_item in tqdm(new_tracks_list):
                coro_tracks: List[Task] = [
                    asyncio.create_task(
                        self.download_tracks(track=track, path=str(path))
                    )
                    for track in tracks_list_item
                ]
                await asyncio.gather(*coro_tracks)

            break


async def main():
    """Main def"""

    client: tuple[ClientAsync] = await asyncio.gather(asyncio.create_task(get_client()))
    app = YandexMusicDownloader(*client)
    print("!DONE")


if __name__ == "__main__":
    asyncio.run(main())
