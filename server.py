from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Token for verifying client (same as used in test.py/local_client.py)
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

# Basic frontend HTML
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>CAN Monitor</title>
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
</head>
<body>
    <h2>Live CAN Data</h2>
    <ul id="log"></ul>

    <script>
        const socket = io();
        const log = document.getElementById("log");

        socket.on("can_message", (data) => {
            const item = document.createElement("li");
            item.textContent = `ID: ${data.id}, Data: ${data.data}, Timestamp: ${data.timestamp}`;
            log.prepend(item);
        });
    </script>
</body>
</html>
"""

# Serve the frontend
@app.route("/")
def index():
    return render_template_string(html_template)

# Receive data from local client
@app.route("/api/send_data", methods=["POST"])
def receive_data():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON"}), 400

    socketio.emit("can_message", data)
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
