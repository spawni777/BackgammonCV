from app import create_app
import os


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 3001))  # Default to 3000 if not set
    app = create_app()

    app.run(debug=True, port=port, host="0.0.0.0")
