from app import create_app, socketio
import os


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 3000))
    app = create_app()

    # app.run(debug=True, port=port, host="0.0.0.0")
    socketio.run(app, port=port, host='0.0.0.0')
