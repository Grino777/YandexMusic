"""App module"""

import os
import sys
from typing import Literal

from yandex_music import ClientAsync

from config import ROOT_DIR
from utils.client import get_client
from utils.colors import Color
from utils.downloader import YandexMusicDownloader
from utils.users import Users, YandexUser


class App:
    """Класс приложения"""

    CHOICES: dict[int, str] = {
        1: "Добавить пользователя в users_list",
        2: "Выбрать пользователя для скачивания плейлистов",
    }

    def __init__(self) -> None:
        self._os_name: str = os.name
        self._clear_command: Literal["clear", "cls"] | None = (
            self._get_clear_cmd_command()
        )
        self.root_dir = ROOT_DIR
        self._users_app = Users()
        self._update_users_list_file()

    def _get_clear_cmd_command(self) -> Literal["clear", "cls"] | None:
        """Получить комманду для очистки консоли в зависимости от системы"""
        match self._os_name:
            case "posix":
                return "clear"
            case "nt":
                return "cls"

    def _update_users_list_file(self):
        """Обновление файла с пользователями"""
        self.yandex_users = self._users_app.get_users()

    async def _find_user_in_yandex_music_api(self):
        """Поиск пользователя в YandexMusic"""

        login: str = input("\nВведите username пользователя: ")

        await self._close_or_restart_app(login)

        user: YandexUser | None = self._users_app.fetching_user_from_api(username=login)

        if isinstance(user, YandexUser):
            self._users_app.add_user(user)
            self._update_users_list_file()
        else:
            await self._find_user_in_yandex_music_api()

    async def _close_or_restart_app(self, user_input):
        """Завершение или перезапуск программы"""

        if user_input.lower() == "q":
            sys.exit()
        if user_input.lower() == "r":
            await self.run_user_selection()

    async def _download_user_playlists(self):
        """Запуск скачивания плейлистов пользователя"""
        user: YandexUser | None = await self.get_user()

        if user:
            client: ClientAsync = await get_client()
            downloader = YandexMusicDownloader(client=client, user=user)

        await downloader.init()

    async def _get_user_selection(self):
        """Получить выбор пользователя"""

        print(
            "\n"
            + Color.UNDERLINE
            + "Управление: Введите 'q' для выхода, 'r' для перезапуска программы\n"
            + Color.ENDC
        )

        for choice_id, choice in self.CHOICES.items():
            print(f"{choice_id}: {choice}", sep="\n")

        user_choice = input("\nВыбирете действие: ")

        await self._close_or_restart_app(user_input=user_choice)

        try:
            user_choice = int(user_choice)

            if user_choice not in self.CHOICES:
                raise ValueError

        except ValueError:
            print("Выбрали неправильное значение!\n")
            await self.run_user_selection()

        if user_choice == 1:
            await self._find_user_in_yandex_music_api()
        if user_choice == 2:
            await self._download_user_playlists()

    async def get_user(self) -> YandexUser | None:
        """Получить пользователя из списка пользователей"""

        for user in self.yandex_users:
            print(f"{user.id}: {user.login}")

        user_id = input(
            "\nВведите id пользователя у которого хотите скачать плейлисты('q' для завершения): "
        )

        await self._close_or_restart_app(user_id)

        user: YandexUser | None = None

        try:
            user_id = int(user_id)
            tmp: list[YandexUser] = [
                user for user in self.yandex_users if user.id == user_id
            ]
            if tmp:
                user = tmp[0]
        except ValueError:
            print("Вы ввели неправильный id пользователя")

        self._update_users_list_file()

        return user

    async def run_user_selection(self) -> YandexUser | None:
        """Функция запуска выбора пользователя"""

        while True:
            await self._get_user_selection()
