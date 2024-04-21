import json
import os

from config import ROOT_DIR
from pydantic import BaseModel


class YandexUser(BaseModel):
    id: int
    name: str
    uid: int


def get_users():
    path = os.path.join(ROOT_DIR, 'users_list', 'users_list.json')

    with open(path, 'r', encoding='utf-8') as file:
        users = json.load(file)

    return users


def add_user():
    path = os.path.join(ROOT_DIR, 'users_list', 'users_list.json')

    with open(path, 'w', encoding='utf-8') as file:
        users = json.load(file)



def converting_users(users: list):
    users = [YandexUser(**user) for user in users]

    return users


yandex_users = get_users() if len(get_users()) == 0 else []

yandex_users = converting_users(yandex_users)
