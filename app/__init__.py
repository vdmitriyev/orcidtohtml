from flask import Flask
from flask_bootstrap import Bootstrap

def create_app(config):

    app = Flask(__name__)
    app.config.from_object(config)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    bootstrap = Bootstrap(app)

    return app
