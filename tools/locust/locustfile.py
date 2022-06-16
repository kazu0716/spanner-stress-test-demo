from random import randint
from time import time
from typing import Dict

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from locust import HttpUser, task

API_VERSION = "v1"
fake = Faker('jp-JP')


class User(BaseModel):
    name: str
    mail: EmailStr
    password: str = Field(min_length=8, max_length=16)


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
        self.headers: Dict[str, str] = {"Content-Type": "application/json", "User-Agent": fake.chrome()}

    @task(1)
    def create_fake_user(self):
        fake_user: User = User(name=fake.name(), mail=fake.email(), password=fake.password(length=randint(8, 16)))
        self.client.post(url=f"/api/{API_VERSION}/users/", headers=self.headers, data=fake_user.json())

    @task(3)
    def create_character(self):
        users = list(self.client.get(url=f"/api/{API_VERSION}/users/", headers=self.headers).json())
        user = users[randint(0, len(users) - 1)]
        characters = list(self.client.get(url=f"/api/{API_VERSION}/character_master/", headers=self.headers).json())
        character = characters[randint(0, len(characters) - 1)]
        fake_character: Character = Character(
            user_id=user["user_id"],
            character_id=character["character_master_id"],
            name=fake.first_kana_name(),
            level=randint(1, 100),
            experience=randint(1, pow(10, 5)),
            strength=randint(1, pow(10, 5))
        )
        self.client.post(url=f"/api/{API_VERSION}/characters/", headers=self.headers, data=fake_character.json())

    @task(10)
    def battle_opponent(self):
        users = list(self.client.get(url=f"/api/{API_VERSION}/users/", headers=self.headers).json())
        user = users[randint(0, len(users) - 1)]
        characters = list(self.client.get(url=f"/api/{API_VERSION}/characters/{user['user_id']}", headers=self.headers).json())
        if not characters:
            return
        character = characters[randint(0, len(characters) - 1)]
        self.client.post(url=f"/api/{API_VERSION}/battles/", headers=self.headers, data={"character_id": character["id"]})

    @task(5)
    def get_histories(self):
        users = list(self.client.get(url=f"/api/{API_VERSION}/users/", headers=self.headers).json())
        user = users[randint(0, len(users) - 1)]
        until = int(time())
        since = until - randint(600, 3600)
        self.client.get(url=f"/api/{API_VERSION}/battles/history?user_id={user['user_id']}&since={since}&until={until}", headers=self.headers)
