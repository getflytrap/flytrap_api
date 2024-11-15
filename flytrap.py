"""Root module for initializing the Flask application.

This script creates an instance of the Flask application by calling the `create_app`
function from the `app` package. The `create_app` function sets up and configures the
application.

Attributes:
    app (Flask): The initialized Flask application instance.
"""

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
