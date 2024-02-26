import json
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

FNAME_FLASK_SECRET_KEY = Path(".flask_secret")


def load_envs():
    """Loads environmental variables from the file"""

    basedir = os.path.abspath(os.path.dirname(__file__))

    if os.environ.get("ENV_FILE") is not None:
        env_file = os.environ.get("ENV_FILE")
        if not os.path.exists(env_file):
            print(f"Give file with environmental variables does not exist: {env_file}")
            load_dotenv(os.path.join(basedir, ".env"))
        else:
            load_dotenv(os.path.join(env_file))
    else:
        load_dotenv(os.path.join(basedir, ".env"))


load_envs()


def random_string(self, size=30):
    import random
    import string

    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(size))


def get_secret_key(fname_secret: str) -> str:
    secret_key = os.environ.get("FLASK_SECRET_KEY")

    if secret_key is None:
        try:
            with open(fname_secret, "r") as _file:
                secret_key = _file.read()
        except FileNotFoundError:
            with open(fname_secret, "w") as _file:
                print(f"Generation new SECRET_KEY. Check: {fname_secret}")
                secret_key = secrets.token_hex(32)
                _file.write(secret_key)
    else:
        with open(fname_secret, "w") as _file:
            _file.write(secret_key)

    return secret_key


class BaseAppConfigs:
    """Defines base configuration for the flask app"""

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print(f"Projects base dir: {BASEDIR}")

    SECRET_KEY = get_secret_key(os.path.join(BASEDIR, FNAME_FLASK_SECRET_KEY))


class DevelopmentConfig(BaseAppConfigs):
    DEBUG = True


class ProductionConfig(BaseAppConfigs):
    DEBUG = False


config_dict = {"development": DevelopmentConfig, "production": ProductionConfig, "default": DevelopmentConfig}
