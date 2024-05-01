"""Downloader module"""

import asyncio
import os
import re

from typing import List

from tqdm import tqdm
from transliterate import translit
from yandex_music import ClientAsync, Playlist, Track, TrackShort, TracksList
from yandex_music.exceptions import (
    InvalidBitrateError,
    TimedOutError,
    UnauthorizedError,
)

from config import ROOT_DIR
from utils.users import YandexUser


class YandexMusicDownloader:
    """Приложение для скачивания музыки"""

    client: ClientAsync
    NAME_MUSIC_FOLDER = "MUSIC"

    def __init__(self, client: ClientAsync, user: YandexUser) -> None:
        self.client = client
        self.root_dir = ROOT_DIR
        self.user: YandexUser = user
        self.user_playlists: dict[str, List[TrackShort]] = {}
        self.user_path = os.path.join(
            self.root_dir, self.NAME_MUSIC_FOLDER, self.user.login.capitalize()
        )

    async def _init(self):
        """Инициализация"""

        self._check_root_music_folder()
        self._check_user_folder()
        await self._get_playlists_user()
        self._create_playlists_folders()

    def _check_root_music_folder(self) -> None:
        """Проверяем наличие корневой папки для музыки"""

        path = os.path.join(self.root_dir, self.NAME_MUSIC_FOLDER)

        if not os.path.exists(path):
            os.makedirs(path)

    def _check_user_folder(self) -> None:
        """Путь до папки пользователя с плейлистами"""

        path = self.user_path

        if not os.path.exists(path):
            os.mkdir(path)

    async def _get_the_favorite_playlist(
        self,
    ) -> dict[str, List[TrackShort] | str] | None:
        """Список треков с отметкой 'Мне нравится'"""

        favorite_playlist: TracksList | None = await self.client.users_likes_tracks(
            user_id=self.user.uid
        )

        if favorite_playlist:
            favorite_tracks: List[TrackShort] = favorite_playlist.tracks

        if isinstance(favorite_tracks, list) and len(favorite_tracks) > 0:
            self.user_playlists.update(
                {
                    "MyFavoritePlaylist": favorite_tracks,
                }
            )

    async def _get_playlists_user(self) -> None:
        """Получить список плейлистов пользователя"""

        await self._get_the_favorite_playlist()

        playlists: List[Playlist] = await self.client.users_playlists_list(
            user_id=self.user.uid
        )

        if len(playlists) > 0:
            for playlist in playlists:
                old_title = str(playlist.title)
                title = old_title.replace("\xa0", " ")
                title = translit(title, language_code="ru", reversed=True)

                self.user_playlists.update({title: playlist.tracks})
        else:
            print("У пользователя нет плейлистов либо они скрыты!")

    def _get_user_playlists_names(self):
        """Получить названия плейлистов пользователя"""

        return list(self.user_playlists)

    def _create_playlists_folders(self) -> None:
        """Создание папок по названию плейлистов"""

        playlist_names = self._get_user_playlists_names()

        for playlist_item in playlist_names:
            path = os.path.join(self.user_path, playlist_item)

            if not os.path.exists(path):
                os.mkdir(path)

    def _get_split_list_of_tracks(self, tracks_list: List[TrackShort]):
        """Функция для разбивки списка на подсписки по 5 треков"""
        
        chunk_size = 5

        for i in range(0, len(tracks_list), chunk_size):
            yield tracks_list[i : i + chunk_size]

    async def _download_tracks(self, track: TrackShort, path: str = "") -> None:
        """Загрузка трека

        Args:
            track (Track): _description_
            path (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """

        error_symbols = r'[\\/:*?"<>\|+]'

        full_track: Track = await track.fetch_track_async()

        filename = f"{full_track.artists[0].name} - {full_track.title}.mp3"
        filename = re.sub(error_symbols, "", filename)
        track_path = str(os.path.join(path, filename))

        result = None

        if not os.path.exists(track_path):
            try:
                result = await full_track.download_async(
                    filename=track_path, codec="mp3", bitrate_in_kbps=320
                )
            except InvalidBitrateError:
                result = await full_track.download_async(
                    filename=track_path,
                    codec="mp3",
                    bitrate_in_kbps=192,
                )
            except TimedOutError:
                await asyncio.sleep(1)
                result = await full_track.download_async(
                    filename=track_path,
                    codec="mp3",
                    bitrate_in_kbps=192,
                )
            except UnauthorizedError:
                pass

            return result
        return result

    async def _download_tracks_from_the_playlist(self) -> None:
        """Скачать треки из плейлистов"""

        for playlist_name, playlist in self.user_playlists.items():
            print(f"Скачивается плейлист: {playlist_name}\n")

            path = os.path.join(self.user_path, playlist_name)

            tracks_list: list[TrackShort] = [item for item in playlist]

            new_tracks_list = list(
                self._get_split_list_of_tracks(tracks_list=tracks_list)
            )

            for tracks_list_item in tqdm(new_tracks_list):
                coro_tracks = [
                    asyncio.create_task(
                        self._download_tracks(track=track, path=str(path))
                    )
                    for track in tracks_list_item
                ]
                await asyncio.gather(*coro_tracks)

        print()

    async def download(self) -> None:
        """Запуск программы"""

        await self._init()
        await self._download_tracks_from_the_playlist()
