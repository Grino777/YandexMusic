"""Модуль для работы с пользователями"""

import json
import os

from typing import Any, Dict
import requests

from requests import Response
from pydantic import BaseModel

from config import ROOT_DIR


class YandexUser(BaseModel):
    """Модель пользователя"""

    id: int
    name: str
    uid: int


def get_users():
    """Получить список пользвателей из users_list.json"""
    path = os.path.join(ROOT_DIR, "users_list.json")

    with open(path, "r", encoding="utf-8") as file:
        users = json.load(file)

    return users


def check_user(username: str):
    """Проверка пользователя по нику"""

    user_uid: int | None = None

    url = f"https://api.music.yandex.net/users/{username}"

    response: Response = requests.get(url=url, timeout=10)

    if response.status_code == 200:
        resp_result: Dict[str, Dict[str, Any]] = response.json()
        result: Dict[str, Any] | None = resp_result.get("result", None)

        if isinstance(result, dict):
            user_uid = result.get("uid")
            
    else:
        print(f"Ошибка {response.status_code} при проверке пользователя {username}")

    return user_uid


def add_user():
    """Добавить пользователя в users_list.json"""

    path = os.path.join(ROOT_DIR, "users_list", "users_list.json")

    with open(path, "w", encoding="utf-8") as file:
        users = json.load(file)


def converting_users(users: list):
    """Конвертировать пользователей в YandexUser"""
    users = [YandexUser(**user) for user in users]

    return users


def get_yandex_users() -> list[YandexUser]:
    """Получить список с Yandex пользователями"""
    
    yandex_users = get_users() if len(get_users()) == 0 else []
    yandex_users = converting_users(yandex_users)

    return yandex_users
