from os import environ, getenv
from uuid import uuid4

from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db() -> Database:
    try:
        if getenv("ENV", "local") == "local":
            environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"
        spanner_client = spanner.Client(project=getenv("GOOGLE_CLOUD_PROJECT", "stress-test-demo"))
        instance = spanner_client.instance(getenv("INSTANCE_NAME", "local"))
        database = instance.database(getenv("DATABASE_NAME", "sample-game"))
        yield database
    finally:
        spanner_client.close()


def get_password_hash(password):
    return context.hash(password)


def get_uuid():
    return uuid4().int & (1 << 63) - 1
