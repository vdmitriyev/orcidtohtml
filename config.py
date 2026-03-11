import logging
import logging.config
import os
import secrets
from datetime import datetime
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


def init_env():
    """Initiate working environment"""
    LOGS_FOLDER = ".logs"
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)


def get_target_server():

    SERVER_MODES = ("dev", "prod")
    TARGET_SERVER_DEFAULT = "dev"
    TARGET_SERVER = os.environ.get("TARGET_SERVER") or "dev"
    if TARGET_SERVER.lower() not in SERVER_MODES:
        print(f"{datetime.now()} error: Invalid <TARGET_SERVER> environmental value. Expected values: {SERVER_MODES}")
        return TARGET_SERVER_DEFAULT

    return TARGET_SERVER


def get_app_config(target_server):
    app_config = None

    if target_server.lower() == "dev":
        from config import DevelopmentConfig

        app_config = DevelopmentConfig
        logging.config.fileConfig(f"configs/logging-{target_server}.conf")

    if target_server.lower() == "prod":
        from config import ProductionConfig

        app_config = ProductionConfig
        logging.config.fileConfig(f"configs/logging-{target_server}.conf")

    return app_config


def change_logging_levels():
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("bibtexparser.customization").setLevel(logging.WARNING)


class BaseAppConfigs:
    """Defines base configuration for the flask app"""

    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    print(f"{datetime.now()} projects base dir: {BASEDIR}")
    DATA_DIR = os.path.join(BASEDIR, os.environ.get("DATA_DIR") or "data")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    SECRET_KEY = get_secret_key(os.path.join(BASEDIR, FNAME_FLASK_SECRET_KEY))


class DevelopmentConfig(BaseAppConfigs):
    DEBUG = True


class ProductionConfig(BaseAppConfigs):
    DEBUG = False
