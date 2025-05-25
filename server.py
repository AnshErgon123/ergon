from server.app import app, socketio
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Only use debug mode in development
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    socketio.run(app, host="0.0.0.0", port=port, debug=debug) 