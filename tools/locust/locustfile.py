from random import randint

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from locust import FastHttpUser, task

API_PATH = "api/v1"
CHARACTER_NUM = 10
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


class StressScenario(FastHttpUser):
    def on_start(self):
        # TODO: create redis connection
        self.headers = {"Content-Type": "application/json"}

    # def on_stop(self):
    #     # TODO: close redis connection
    #     pass

    @task(1)
    def create_fake_user(self):
        self.headers["User-Agent"] = fake.chrome()
        fake_user = User(name=fake.name(), mail=fake.email(), password=fake.password(length=randint(8, 16)))
        self.client.post(url=f"/{API_PATH}/users/", headers=self.headers, data=fake_user.json())
        # TODO: Stored user id to redis

    @task(1)
    def create_character(self):
        self.headers["User-Agent"] = fake.chrome()
        # TODO: GET USER ID
        fake_character = Character(
            user_id=randint(8, 16),
            character_id=randint(1, CHARACTER_NUM),
            name=fake.first_kana_name(),
            level=1,
            experience=0,
            strength=0
        )
        self.client.post(url=f"/{API_PATH}/characters/", headers=self.headers, data=fake_character.json())
        # TODO: Stored character id to redis

    @task(1)
    def battle_opponent(self):
        # TODO: get character
        pass

    @task(1)
    def get_histories(self):
        # TODO: get character
        pass
