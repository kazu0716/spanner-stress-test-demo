from datetime import datetime, timedelta, timezone
from os import environ, getenv
from time import time_ns
from uuid import uuid4

from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# NOTE: Spanner Settings
PROJECT: str = getenv("GOOGLE_CLOUD_PROJECT", "stress-test-demo")
INSTANCE: str = getenv("INSTANCE_NAME", "local")
DATABASE: str = getenv("DATABASE_NAME", "sample-game")


def get_db() -> Database:
    try:
        # NOTE: set host path to spanner own emulator in local env
        if getenv("ENV", "local") == "local":
            environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"
        spanner_client = spanner.Client(project=PROJECT)
        instance = spanner_client.instance(INSTANCE)
        database = instance.database(DATABASE)
        yield database
    finally:
        spanner_client.close()


def get_password_hash(password):
    return context.hash(password)


def get_uuid() -> int:
    return uuid4().int & (1 << 63) - 1


def get_entry_shard_id(user_id: int) -> int:
    num_shards = 100
    now: int = time_ns() // 1000
    return (user_id + now + get_uuid()) % num_shards


def epoch_to_datetime(epoch: int) -> str:
    # TODO: consider how to handle timestamp
    return datetime.fromtimestamp(epoch).isoformat() + "Z"
