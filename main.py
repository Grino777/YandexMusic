# coding=utf-8

"""Download music app"""

import asyncio
import os
import re
import sys
from asyncio import Task
from typing import Dict, List

from tqdm import tqdm
from transliterate import translit
from yandex_music import ClientAsync, Playlist, TrackShort, TracksList
from yandex_music.exceptions import (
    InvalidBitrateError,
    TimedOutError,
    UnauthorizedError,
)
from yandex_music.track.track import Track

from utils.client import get_client
from utils.users import YandexUser, yandex_users

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class YandexMusicDownloader:
    """Приложение для скачивания музыки"""

    client: ClientAsync

    ROOT_DIRECTORY = os.path.dirname((os.path.realpath(__file__)))
    NAME_MUSIC_FOLDER = "MUSIC"

    def __init__(self, client: ClientAsync, user: YandexUser) -> None:
        self.client = client
        self.user_uid = user.uid
        self.user_name = user.name.capitalize()
        self.user_directory = self._get_user_directory()
        self.user_playlists: List[Dict[str, Playlist]] = []

    def _get_user_directory(self) -> str:
        path = os.path.join(self.ROOT_DIRECTORY, self.NAME_MUSIC_FOLDER, self.user_name)
        return path

    def _get_split_list_of_tracks(self, tracks_list: List):
        """Функция для разбивки списка на подсписки по 5 треков"""
        chunk_size = 5

        for i in range(0, len(tracks_list), chunk_size):
            yield tracks_list[i : i + chunk_size]

    def _create_username_folder(self) -> None:
        path = os.path.join(self.ROOT_DIRECTORY, self.NAME_MUSIC_FOLDER, self.user_name)
        if not os.path.exists(path):
            os.makedirs(path)

    def _create_playlists_folders(self) -> None:
        """Создание папок по названию плейлистов"""
        user_directory = self.user_directory

        for playlist_item in self.user_playlists:
            path = os.path.join(user_directory, playlist_item.get("title"))  # type: ignore
            if not os.path.exists(path):
                os.mkdir(path)

    async def _get_the_favorite_playlist(self):
        """Получить список треков с отметкой 'Мне нравится'"""

        favorite_playlist: TracksList | None = await self.client.users_likes_tracks(
            user_id=self.user_uid
        )
        tracks_list: List[TrackShort] = favorite_playlist.tracks  # pyright: ignore[reportOptionalMemberAccess]
        print(tracks_list)

    async def _get_playlists_user(self) -> None:
        """Получить список плейлистов пользователя"""

        user_playlists = await self.client.users_playlists_list(user_id=self.user_uid)

        if len(user_playlists) > 0:
            for playlist in user_playlists:
                old_title = str(playlist.title)
                title = old_title.replace("\xa0", " ")
                title = translit(title, language_code="ru", reversed=True)

                self.user_playlists.append({"title": title, "playlist": playlist})
        else:
            print("У пользователя нет плейлистов либо они скрыты!")

    def _check_current_directory(self):
        """Проверка директории на наличие корневой папки music"""

        if not os.path.exists(self.NAME_MUSIC_FOLDER):
            os.makedirs(self.NAME_MUSIC_FOLDER)

    async def _download_tracks_from_the_playlist(self):
        """Скачать треки из плейлистов"""

        for playlist_item in self.user_playlists:
            print(f"Скачивается плейлист: {playlist_item.get('title')}\n")

            tracks_list: List[TrackShort] = []

            path = os.path.join(self.user_directory, playlist_item["title"])  # type: ignore
            playlist: Playlist = playlist_item.get("playlist")  # type:ignore
            tracks_list.extend(await playlist.fetch_tracks_async())
            tracks: List[Track | None] = [item.track for item in tracks_list]

            new_tracks_list = list(self._get_split_list_of_tracks(tracks_list=tracks))

            for tracks_list_item in tqdm(new_tracks_list):
                coro_tracks: List[Task] = [
                    asyncio.create_task(
                        self._download_tracks(track=track, path=str(path))
                    )
                    for track in tracks_list_item
                ]
                await asyncio.gather(*coro_tracks)

    async def _download_tracks(self, track: Track, path: str = "") -> None:
        """Загрузка трека"""

        error_symbols = r'[\\/:*?"<>\|+]'

        filename = f"{track.artists[0].name} - {track.title}.mp3"
        filename = re.sub(error_symbols, "", filename)
        track_path = str(os.path.join(path, filename))

        result = None

        if not os.path.exists(track_path):
            try:
                result = await track.download_async(
                    filename=track_path, codec="mp3", bitrate_in_kbps=320
                )
            except InvalidBitrateError:
                result = await track.download_async(
                    filename=track_path,
                    codec="mp3",
                    bitrate_in_kbps=192,
                )
            except TimedOutError:
                await asyncio.sleep(1)
                result = await track.download_async(
                    filename=track_path,
                    codec="mp3",
                    bitrate_in_kbps=192,
                )
            except UnauthorizedError:
                pass

            return result
        return result

    async def init(self) -> None:
        """Инициализация"""

        self._check_current_directory()
        self._create_username_folder()
        await self._get_playlists_user()
        self._create_playlists_folders()
        await self._download_tracks_from_the_playlist()


class App:
    """Класс приложения"""

    CHOICES: dict[int, str] = {
        1: "Добавить пользователя в users_list",
        2: "Выбрать пользователя для скачивания плейлистов",
    }
    
    SYSTEM = os.name

    def _check_user_uid(self) -> YandexUser | None:
        """Получить user data"""

        user_id = input("Введите ID: ")

        if user_id == "q":
            sys.exit()

        try:
            user_id = int(user_id)
        except ValueError:
            print("Вы ввели неправильный ID или ввели строку!")

        for client in yandex_users:
            if user_id == client.id:
                result = client

        return result

    def _get_user(self) -> YandexUser | None:
        """Функция запуска выбора пользователя"""

        if self.SYSTEM == 'nt':
            os.system("cls")
        if self.SYSTEM == 'posix':
            os.system("clear")

        print("Выберете ID пользователя у которого хотите скачать плейлисты, либо наэмите 'q' для выхода")

        for client in yandex_users:
            print(f"{client.name.capitalize()}: {client.id}", sep="\n")
        print()

        while True:
            user: YandexUser | None = self._check_user_uid()
            if user:
                return user

    # def run_user_selection(self) -> YandexUser:

    def run_user_selection(self) -> YandexUser | None:
        """Функция запуска выбора пользователя"""

        for choice_id, choice in self.CHOICES.items():
            print(f"{choice_id}: {choice}", sep="\n")

        user_choice = input("Выберете действие: ")

        try:
            user_choice = int(user_choice)

            if user_choice not in self.CHOICES:
                raise ValueError

        except ValueError:
            print("Выбрали неправильное значение!\n")
            self.run_user_selection()

        if user_choice == 1:
            pass
        if user_choice == 2:
            user = self._get_user()
            return user
        if user_choice == "q":
            sys.exit()


async def main():
    """Main def"""

    app = App()

    user = app.run_user_selection()

    if user:
        client: ClientAsync = await get_client()

        downloader = YandexMusicDownloader(client=client, user=user)
        await downloader.init()
        # await app._get_the_favorite_playlist()

    print("DONE!")


if __name__ == "__main__":
    asyncio.run(main())
