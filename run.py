import logging

from config import get_app_config, get_target_server, init_env, load_envs

load_envs()
init_env()
app_config = get_app_config(get_target_server())

from app import create_app

app = create_app(app_config)

logger = logging.getLogger("app")
app.logger.handlers = logger.handlers

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5151, debug=True)
