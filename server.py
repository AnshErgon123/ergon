from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import os, time

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/send_data", methods=["POST"])
def receive_data():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split()[1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    socketio.emit("can_message", data)
    return jsonify({"status": "received"}), 200

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split()[1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json() or {}
    status = payload.get("status", "offline")
    socketio.emit("heartbeat", {"status": status, "ts": time.time()})
    return jsonify({"status": "ok"}), 200

@socketio.on("connect")
def on_connect():
    print("Web client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Web client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
