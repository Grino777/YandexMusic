"""Модуль для работы с пользователями"""

import json
import os
from typing import Any, Dict, List

import requests
from pydantic import BaseModel
from requests import Response

from config import ROOT_DIR
from utils.colors import Color


class YandexUser(BaseModel):
    """Модель пользователя"""

    id: int | None = None
    login: str
    uid: int

    def __hash__(self) -> int:
        return hash((self.login, self.uid))

    def __eq__(self, user) -> bool:
        return hash(self) == hash(user)


class Users:
    """Класс для работы с пользователями и файлом пользователей"""

    def __init__(self) -> None:
        self._check_users_list_file()
        self.users_list_file = os.path.join(ROOT_DIR, "users_list.json")
        self.users: List[YandexUser] = self.get_users()

    def _check_users_list_file(self) -> None:
        """Проверка налчия файла с пользователями в корневой папке"""

        path = os.path.join(ROOT_DIR, "users_list.json")

        if not os.path.exists(path):
            data = {"users_counter": 0, "users": []}

            with open(path, "w", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))

    def _save_users_list_file(self, users_obj: dict) -> None:
        """Перезапись файла с пользователями"""

        with open(self.users_list_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(dict(users_obj), indent=4, ensure_ascii=False))

    def _json_to_dict(self) -> Dict[str, Any]:
        """Получить python object из users_list.json"""

        with open(self.users_list_file, "r", encoding="utf-8") as file:
            users_obj: Dict = json.load(file)

        return users_obj

    def _update_counter_and_ids(self, users_obj: dict) -> None:
        """Обновить id пользователей и счетчик пользователей в users_list.json"""

        users_obj["users_counter"] = len(users_obj["users"])

        for i in range(users_obj["users_counter"]):
            user = users_obj["users"][i]
            user["id"] = i + 1

        self._save_users_list_file(users_obj)

    def add_user(self, user: YandexUser) -> None:
        """Добавить пользователя в users_list.json"""

        json_data = self._json_to_dict()
        yandex_users: List[YandexUser] = self.get_users()

        if user in yandex_users:
            print(Color.OKGREEN + "Пользователь уже есть в списке!\n" + Color.ENDC)
        else:
            user_obj = user.model_dump()
            json_data["users"].append(user_obj)
            self._update_counter_and_ids(json_data)

            print(
                f"Пользователь: {user.login.capitalize()} с id: {user.uid} успешно добавлен."
            )

    def remove_user(self, user_id: int) -> None:
        """Удаление пользователя из users_list.json"""

        users_obj = self._json_to_dict()

        users_obj["users"] = [
            user for user in users_obj["users"] if user["id"] != user_id
        ]

        self._update_counter_and_ids(users_obj=users_obj)

        print("Пользователь успешно удален!")

    def get_user(self, user_id: int) -> YandexUser:
        """Получить объект пользователя"""

        users: List[YandexUser] = self.get_users()

        user: list[YandexUser] = [user for user in users if user_id == user.id]

        if user is None:
            print("Пользователь не найден")
            return YandexUser(login="", uid=0)
        else:
            return user[0]

    def get_users(self) -> List[YandexUser]:
        """Получить объекты пользователей"""

        users_obj: Dict[str, list[Any]] = self._json_to_dict()
        users_list: list[Any] = users_obj["users"]

        users: List[YandexUser] = [YandexUser(**user) for user in users_list]
        return users

    @staticmethod
    def fetching_user_from_api(username: str) -> YandexUser | None:
        """Поиск пользователя в YandexMusic"""

        user: YandexUser | None = None

        url = f"https://api.music.yandex.net/users/{username}"

        response: Response = requests.get(url=url)

        if response.status_code == 200:
            resp_result = response.json()
            result = resp_result.get("result")

            if isinstance(result, dict):
                user = YandexUser(**result)
        else:
            print(f"Ошибка {response.status_code} при проверке пользователя {username}")

        return user
