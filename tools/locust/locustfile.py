import logging
from random import randint
from time import time
from typing import Dict

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from locust import HttpUser, task

# NOTE: logging settings
# TODO: adjust following for cloud logging format
Log_Format = "%(thread)d %(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(format=Log_Format, level=logging.DEBUG)
logger = logging.getLogger()
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
    def on_start(self):
        self.version = "v1"
        self.headers: Dict[str, str] = {"Content-Type": "application/json", "User-Agent": fake.chrome()}

    @task(1)
    def create_fake_user(self):
        """create game user"""
        logger.info("start create_fake_user")
        fake_user: User = User(name=fake.name(), mail=fake.email(), password=fake.password(length=randint(8, 16)))
        res = self.client.post(url=f"/api/{self.version}/users/", headers=self.headers, data=fake_user.json()).json()
        logger.info(f"user: {res}")
        logger.info("end create_fake_user")

    @task(3)
    def create_character(self):
        """a random user to get a random character"""
        logger.info("start create_character")
        user = self.client.get(url=f"/api/{self.version}/users/", headers=self.headers).json()
        logger.info(f"user: {user}")
        character = self.client.get(url=f"/api/{self.version}/character_master/", headers=self.headers).json()
        logger.info(f"character master: {character}")
        fake_character: Character = Character(
            user_id=user["user_id"],
            character_id=character["character_master_id"],
            name=fake.first_kana_name(),
            level=randint(1, 100),
            experience=randint(1, pow(10, 5)),
            strength=randint(1, pow(10, 5))
        )
        res = self.client.post(url=f"/api/{self.version}/characters/", headers=self.headers, data=fake_character.json()).json()
        logger.info(f"result: {res}")
        logger.info("end create_character")

    @task(10)
    def battle_opponent(self):
        """a random user to battle a random opponent"""
        logger.info("start battle_opponent")
        user = self.client.get(url=f"/api/{self.version}/users/", headers=self.headers).json()
        logger.info(f"user: {user}")
        characters = list(self.client.get(url=f"/api/{self.version}/characters/{user['user_id']}", headers=self.headers).json())
        if "detail" in characters:
            logger.info("re-get character for battle")
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
        logger.info(f"characters length: {len(characters)}")
        character = characters[randint(0, len(characters) - 1)]
        logger.info(f"character: {character}")
        battle = Battles(character_id=character["id"])
        res = self.client.post(url=f"/api/{self.version}/battles/", headers=self.headers, data=battle.json()).json()
        logger.info(f"result: {res}")
        logger.info("end battle_opponent")

    @task(5)
    def get_histories(self):
        """get a battle history between random range"""
        logger.info("start get_histories")
        user = self.client.get(url=f"/api/{self.version}/users/", headers=self.headers).json()
        until = int(time())
        since = until - randint(600, 3600)
        logger.info(f"user: {user['user_id']}, since: {since}, until: {until}")
        res = self.client.get(
            url=f"/api/{self.version}/battles/history?user_id={user['user_id']}&since={since}&until={until}", headers=self.headers).json()
        logger.info(f"result: {res}")
        logger.info("end get_histories")
