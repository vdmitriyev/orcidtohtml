import os
import json
from dotenv import load_dotenv

def load_envs():
    ''' Loads environmental variables from the file'''

    basedir = os.path.abspath(os.path.dirname(__file__))

    if os.environ.get('ENV_FILE') is not None:
        env_file = os.environ.get('ENV_FILE')
        if not os.path.exists(env_file):
            print (f'Give file with environmental variables does not exist: {env_file}')
            load_dotenv(os.path.join(basedir, '.env'))
        else:
            load_dotenv(os.path.join(env_file))
    else:
        load_dotenv(os.path.join(basedir, '.env'))

load_envs()

def random_string(self, size=30):
    import random, string
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(size))

class BaseAppConfigs:
    '''Defines base configuration for the flask app '''

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print(f'Projects base dir: {BASEDIR}')

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or random_string(30)

class DevelopmentConfig(BaseAppConfigs):
    DEBUG = True

class ProductionConfig(BaseAppConfigs):
    DEBUG = False

config_dict = {
    'development'   : DevelopmentConfig,
    'production'    : ProductionConfig,
    'default'       : DevelopmentConfig
}

