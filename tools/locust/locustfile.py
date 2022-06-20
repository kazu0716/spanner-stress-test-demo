import logging
from os import getenv
from random import randint
from time import time
from typing import Dict

import requests
from faker import Faker
from google.cloud.logging import Client
from pydantic import BaseModel, EmailStr, Field

from locust import HttpUser, task

ENV = getenv("ENV", "local")
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")

# NOTE: logging settings
if ENV == "production":
    client = Client()
    client.setup_logging()
else:
    logging.basicConfig(format="%(asctime)s %(thread)d %(funcName)s %(levelname)s %(message)s", level=logging.getLevelName(LOG_LEVEL))
logger = logging.getLogger()
logger.setLevel(logging.getLevelName(LOG_LEVEL))

fake = Faker('jp-JP')

class User(BaseModel):
    name: str
    mail: EmailStr
    password: str = Field(min_length=8, max_length=16)


class Battles(BaseModel):
    character_id: int


class Character(BaseModel):
    user_id: int
    character_id: int
    name: str
    level: int
    experience: int
    strength: int


class UpdateCharacters(BaseModel):
    id: int
    level: int
    experience: int

class StressScenario(HttpUser):
    def __init__(self, parent):
        super().__init__(parent)
        # NOTE: get users before tests
        logger.debug("load users info")
        self.users = self.client.get(url=f"/api/v1/users/", headers={"Content-Type": "application/json", "User-Agent": fake.chrome()}).json()
        logger.debug("end users info")

    def on_start(self):
        self.version = "v1"
        self.headers: Dict[str, str] = {"Content-Type": "application/json", "User-Agent": fake.chrome()}
        if not self.users:
            self.users = self.client.get(url=f"/api/{self.version}/users/", headers=self.headers).json()

    @ task(1)
    def create_fake_user(self):
        """create game user"""
        logger.debug("start create_fake_user")
        fake_user: User = User(name=fake.name(), mail=fake.email(), password=fake.password(length=randint(8, 16)))
        res = self.client.post(url=f"/api/{self.version}/users/", headers=self.headers, data=fake_user.json()).json()
        logger.debug(f"user: {res}")
        logger.debug("end create_fake_user")

    @ task(3)
    def create_character(self):
        """a random user to get a random character"""
        logger.debug("start create_character")
        user = dict(self.users[randint(0, len(self.users))])
        logger.debug(f"user: {user}")
        character = self.client.get(url=f"/api/{self.version}/character_master/", headers=self.headers).json()
        logger.debug(f"character master: {character}")
        fake_character: Character = Character(
            user_id=user["user_id"],
            character_id=character["character_master_id"],
            name=fake.first_kana_name(),
            level=randint(1, 100),
            experience=randint(1, pow(10, 5)),
            strength=randint(1, pow(10, 5))
        )
        res = self.client.post(url=f"/api/{self.version}/characters/", headers=self.headers, data=fake_character.json()).json()
        logger.debug(f"result: {res}")
        logger.debug("end create_character")

    @task(10)
    def battle_opponent(self):
        """a random user to battle a random opponent"""
        logger.debug("start battle_opponent")
        user = dict(self.users[randint(0, len(self.users))])
        logger.debug(f"user: {user}")
        characters = list(self.client.get(url=f"/api/{self.version}/characters/{user['user_id']}", headers=self.headers).json())
        if "detail" in characters:
            logger.debug("re-get character for battle")
            character = self.client.get(url=f"/api/{self.version}/character_master/", headers=self.headers).json()
            fake_character: Character = Character(
                user_id=user["user_id"],
                character_id=character["character_master_id"],
                name=fake.first_kana_name(),
                level=randint(1, 100),
                experience=randint(1, pow(10, 5)),
                strength=randint(1, pow(10, 5))
            )
            self.client.post(url=f"/api/{self.version}/characters/", headers=self.headers, data=fake_character.json()).json()
            characters = list(self.client.get(url=f"/api/{self.version}/characters/{user['user_id']}", headers=self.headers).json())
        logger.debug(f"characters length: {len(characters)}")
        character = characters[randint(0, len(characters) - 1)]
        logger.debug(f"character: {character}")
        battle = Battles(character_id=character["id"])
        res = self.client.post(url=f"/api/{self.version}/battles/", headers=self.headers, data=battle.json()).json()
        logger.debug(f"result: {res}")
        logger.debug("end battle_opponent")

    @task(5)
    def get_histories(self):
        """get a battle history between random range"""
        logger.debug("start get_histories")
        user = dict(self.users[randint(0, len(self.users))])
        until = int(time())
        since = until - randint(600, 3600)
        logger.debug(f"user: {user['user_id']}, since: {since}, until: {until}")
        res = self.client.get(
            url=f"/api/{self.version}/battles/history?user_id={user['user_id']}&since={since}&until={until}", headers=self.headers).json()
        logger.debug(f"result: {res}")
        logger.debug("end get_histories")
