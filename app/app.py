"""App module"""

import json
import os
from typing import Literal

from users.users import YandexUser, get_yandex_users
from config import ROOT_DIR


class App:
    """Класс приложения"""

    CHOICES: dict[int, str] = {
        1: "Добавить пользователя в users_list",
        2: "Выбрать пользователя для скачивания плейлистов",
    }

    def __init__(self):
        self.os_name = os.name
        self._check_users_list_file()
        self.users_list_file = os.path.join(ROOT_DIR, "users_list.json")
        self.yandex_users: list[YandexUser] = get_yandex_users()

    # def _check_user_uid(self) -> YandexUser | None:
    #     """Получить user data"""

    #     user_id = input("Введите ID: ")
    #     yandex_users: list[YandexUser] = self.yandex_users

    #     if user_id == "q":
    #         sys.exit()

    #     try:
    #         user_id = int(user_id)
    #     except ValueError:
    #         print("Вы ввели неправильный ID или ввели строку!")

    #     for client in yandex_users:
    #         if user_id == client.id:
    #             result: YandexUser = client

    #     return result

    # def _get_user(self) -> YandexUser | None:
    #     """Функция запуска выбора пользователя"""

    #     yandex_users: list[YandexUser] = self.yandex_users

    #     if self.SYSTEM == "nt":
    #         os.system("cls")
    #     if self.SYSTEM == "posix":
    #         os.system("clear")

    #     print(
    #         "Выберете ID пользователя у которого хотите скачать плейлисты, либо наэмите 'q' для выхода"
    #     )

    #     for client in yandex_users:
    #         print(f"{client.name.capitalize()}: {client.id}", sep="\n")
    #     print()

    #     while True:
    #         user: YandexUser | None = self._check_user_uid()
    #         if user:
    #             return user

    # # def run_user_selection(self) -> YandexUser:

    # def run_user_selection(self) -> YandexUser | None:
    #     """Функция запуска выбора пользователя"""

    #     for choice_id, choice in self.CHOICES.items():
    #         print(f"{choice_id}: {choice}", sep="\n")

    #     user_choice = input("Выберете действие: ")

    #     try:
    #         user_choice = int(user_choice)

    #         if user_choice not in self.CHOICES:
    #             raise ValueError

    #     except ValueError:
    #         print("Выбрали неправильное значение!\n")
    #         self.run_user_selection()

    #     if user_choice == 1:
    #         pass
    #     if user_choice == 2:
    #         user = self._get_user()
    #         return user
    #     if user_choice == "q":
    #         sys.exit()

    def _check_user_uid(self, uid: int | str):
        pass

    def _get_clear_cmd_command(self) -> Literal["clear", "cls"] | None:
        """Получить комманду для очистки консоли в зависимости от системы"""
        match self.os_name:
            case "posix":
                return "clear"
            case "nt":
                return "cls"

    def _rewrite_users_list_file(self, user_obj: dict):
        """Перезаписать файл с пользователями"""
        with open(self.users_list_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(dict(user_obj), indent=4, ensure_ascii=False))

    def _check_users_list_file(self):
        """Проверка налчия файла с пользователями в корневой папке"""

        path = os.path.join(ROOT_DIR, "users_list.json")

        if not os.path.exists(path):
            data = {"users_counter": 0, "users": []}

            with open(path, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))

    def _json_to_dict(self):
        """Получить python object из users_list.json"""

        with open(self.users_list_file, "r", encoding="utf-8") as file:
            users_obj = json.load(file)

        return users_obj

    def add_user(self, user: YandexUser):
        """Добавить пользователя в users_list.json"""
        json_data = self._json_to_dict()

        user_obj = {'id': json_data['id'] + 1, 'name': user.name, 'uid': user.uid}

        json_data["users_counter"] = + 1
        json_data["users"].append(user_obj)

        self._rewrite_users_list_file(json_data)

    def get_user(self, id: int):
        """Получить объект пользователя"""
        pass

    def get_users(self):
        """Получить объекты пользователей"""
        pass

    def get_user_uid(self, uid: int):
        """Получить uid определенного пользователя"""
        pass
