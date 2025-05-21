from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
import os
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")
last_heartbeat_time = 0

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CAN Bus Live Monitor</title>
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        nav {
            background-color: #1e88e5;
            padding: 1rem 2rem;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        nav h1 {
            margin: 0;
            font-size: 1.5rem;
        }

        nav .status {
            font-size: 0.9rem;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            background-color: #c62828;
        }

        nav .status.connected {
            background-color: #2e7d32;
        }

        main {
            flex: 1;
            padding: 2rem;
        }

        h2 {
            margin-bottom: 1rem;
        }

        .search-box {
            margin-bottom: 1rem;
        }

        .search-box input {
            padding: 0.5rem;
            font-size: 1rem;
            width: 100%;
            max-width: 300px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }

        thead {
            background-color: #1976d2;
            color: white;
        }

        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
            font-family: monospace;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tbody tr:nth-child(even) {
            background-color: #f1f1f1;
        }

        footer {
            background-color: #1e88e5;
            color: white;
            text-align: center;
            padding: 1rem;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            th, td {
                font-size: 0.85rem;
            }
        }
    </style>
</head>
<body>
    <nav>
        <h1>CAN Monitor Dashboard</h1>
        <div class="status" id="status">Disconnected</div>
    </nav>

    <main>
        <h2>Live CAN Data</h2>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Filter by CAN ID or Data...">
        </div>

        <table>
            <thead>
                <tr>
                    <th>CAN ID</th>
                    <th>Data</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody id="log">
                <!-- CAN data rows will be injected here -->
            </tbody>
        </table>
    </main>

    <footer>
        CAN Monitor | by Ergon Mobility 
    </footer>

    <script>
        const socket = io();
        const log = document.getElementById("log");
        const status = document.getElementById("status");
        const searchInput = document.getElementById("searchInput");
        const maxRows = 100;
        let allMessages = [];
        let heartbeatTimeout;

        socket.on("connect", () => {
            console.log("Socket.IO connected");
        });

        socket.on("disconnect", () => {
            console.log("Socket.IO disconnected");
            setClientStatus("Disconnected");
        });

        socket.on("can_message", (data) => {
            allMessages.unshift(data);
            if (allMessages.length > maxRows) {
                allMessages.pop();
            }
            renderMessages();
        });

        socket.on("heartbeat", (data) => {
            setClientStatus("Connected");
            clearTimeout(heartbeatTimeout);
            heartbeatTimeout = setTimeout(() => {
                setClientStatus("Disconnected");
            }, 10000);
        });

        searchInput.addEventListener("input", renderMessages);

        function renderMessages() {
            const filter = searchInput.value.toLowerCase();
            log.innerHTML = "";
            const filtered = allMessages.filter(msg =>
                msg.id.toLowerCase().includes(filter) ||
                msg.data.toLowerCase().includes(filter)
            );
            for (const data of filtered) {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${data.id}</td>
                    <td>${data.data}</td>
                    <td>${data.timestamp}</td>
                `;
                log.appendChild(row);
            }
        }

        function setClientStatus(text) {
            status.textContent = text;
            status.classList.toggle("connected", text === "Connected");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_template)

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

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    global last_heartbeat_time
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    last_heartbeat_time = time.time()
    socketio.emit("heartbeat", {"status": "online", "timestamp": last_heartbeat_time})
    return jsonify({"status": "alive"}), 200

@socketio.on("connect")
def on_connect():
    print("Web client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Web client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
