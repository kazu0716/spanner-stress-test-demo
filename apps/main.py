import logging
import os
from os import getenv
from sys import stdout

from fastapi import FastAPI
from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger
from loguru import logger

from routers.battles import router as battle_router
from routers.character_master import router as character_master_router
from routers.characters import router as characters_router
from routers.opponent_master import router as opponent_master_router
from routers.users import router as user_router

# NOTE: settings from env values
ENV = getenv("ENV", "local")
LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False
WORKERS = int(os.environ.get("GUNICORN_WORKERS", "4"))

app = FastAPI()
# NOTE: API version 1
prefix_v1 = "/api/v1"
app.include_router(user_router, prefix=prefix_v1)
app.include_router(characters_router, prefix=prefix_v1)
app.include_router(character_master_router, prefix=prefix_v1)
app.include_router(opponent_master_router, prefix=prefix_v1)
app.include_router(battle_router, prefix=prefix_v1)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOG_LEVEL)
        self.access_logger.setLevel(LOG_LEVEL)


class StandaloneApplication(BaseApplication):
    """Our Gunicorn application."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    # NOTE: gunicorn and uvicorn settings
    # ref: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": stdout, "serialize": JSON_LOGS}])

    options = {
        "bind": "0.0.0.0",
        "workers": WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger
    }

    StandaloneApplication(app, options).run()
