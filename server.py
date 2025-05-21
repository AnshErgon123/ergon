from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Token for verifying client (same as used in test.py/local_client.py)
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CAN Bus Live Monitor</title>
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }

        header {
            background-color: #1e88e5;
            color: white;
            padding: 1rem;
            text-align: center;
        }

        main {
            padding: 1rem 2rem;
        }

        h2 {
            margin-bottom: 1rem;
        }

        #log {
            list-style: none;
            padding: 0;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #ccc;
            background-color: white;
            border-radius: 6px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        #log li {
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #eee;
            font-family: monospace;
        }

        #log li:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <header>
        <h1>CAN Bus Live Monitor</h1>
    </header>
    <main>
        <h2>Live CAN Data</h2>
        <ul id="log"></ul>
    </main>

    <script>
        const socket = io();
        const log = document.getElementById("log");
        const maxEntries = 200;

        socket.on("can_message", (data) => {
            const item = document.createElement("li");
            item.textContent = `ID: ${data.id}, Data: ${data.data}, Timestamp: ${data.timestamp}`;
            log.prepend(item);

            // Keep log length under maxEntries
            while (log.children.length > maxEntries) {
                log.removeChild(log.lastChild);
            }
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
