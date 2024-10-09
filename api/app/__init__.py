from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Store the root path in the configuration
    app.config['ROOT_PATH'] = app.root_path

    # Enable CORS for the entire app
    CORS(app)

    # Register API routes
    from .routes import user_routes
    app.register_blueprint(user_routes.bp)

    from .routes import backgammon_routes
    app.register_blueprint(backgammon_routes.bp)

    # Register template routes
    from .routes import template_routes
    app.register_blueprint(template_routes.bp)

    return app
