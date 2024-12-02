"""Root module for initializing the Flask application.

This script creates an instance of the Flask application by calling the `create_app`
function from the `app` package. The `create_app` function sets up and configures the
application.

Attributes:
    app (Flask): The initialized Flask application instance.
"""

import logging
import atexit
from app import create_app, socketio
from config import load_config
from db import init_db_pool, close_db_pool

logging.basicConfig(
    level=logging.INFO,  # Default to INFO for initial setup
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = create_app()
load_config(app)
init_db_pool(app)

environment = app.config.get("ENVIRONMENT")
if environment == "development":
    app.logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)

atexit.register(close_db_pool)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
