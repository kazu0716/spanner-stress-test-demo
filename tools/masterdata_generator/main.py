from argparse import ArgumentParser
from random import randint
from typing import Dict

import requests
from faker import Faker
from pydantic import BaseModel

fake = Faker('jp-JP')


class CharacterMaster(BaseModel):
    name: str
    kind: str


class OpponentMaster(BaseModel):
    name: str
    kind: str
    strength: int
    experience: int


def load_masters(args):
    API_VERSION = args.version
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    host = ("https://" if args.https else "http://") + args.target + ":" + args.port
    # NOTE: add character masters
    for _ in range(args.line):
        fake_character_master = CharacterMaster(name=fake.first_kana_name(), kind="fake")
        res = requests.post(url=f"{host}/api/{API_VERSION}/character_master/", headers=headers, data=fake_character_master.json())
        print(res.json())
    # NOTE: add opponent masters
    for _ in range(args.line):
        fake_opponent_master = OpponentMaster(name=fake.first_kana_name(), kind="fake",
                                              strength=randint(1, pow(10, 5)), experience=randint(1, pow(10, 5)))
        res = requests.post(url=f"{host}/api/{API_VERSION}/opponent_master/", headers=headers, data=fake_opponent_master.json())
        print(res.json())


if __name__ == "__main__":
    parser = ArgumentParser(description="importer master data for stress test")
    parser.add_argument('-t', '--target', default='localhost', type=str, help='target host')
    parser.add_argument('-p', '--port', default='8000', type=str, help='target port')
    parser.add_argument('-l', '--line', default=100, type=int, help='number of master data')
    parser.add_argument('-v', '--version', default="v1", type=str, help='target api version')
    parser.add_argument('--https', default=False, type=bool, help='target https')
    load_masters(parser.parse_args())
