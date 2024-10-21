from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
# import eventlet

# eventlet.monkey_patch()  # Patches to ensure async handling

# Initialize the SocketIO instance (with CORS support)
socketio = SocketIO(cors_allowed_origins="*")  # Adjust as needed for specific origins

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

    # Initialize the app with SocketIO  
    socketio.init_app(app)

    return app
