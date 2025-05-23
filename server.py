from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
import os, time

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

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

        main {
            flex: 1;
            padding: 2rem;
        }

        h2 {
            margin-bottom: 1rem;
        }

        .controls {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .controls input {
            padding: 0.5rem 1rem;
            font-size: 1rem;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .controls button {
            padding: 0.5rem 1.2rem;
            font-size: 1rem;
            border: none;
            border-radius: 5px;
            background-color: #1976d2;
            color: white;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .controls button:hover {
            background-color: #1565c0;
        }

        .controls button:active {
            background-color: #0d47a1;
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

            .controls {
                flex-direction: column;
                align-items: stretch;
            }

            .controls input, .controls button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <nav>
        <h1>CAN Monitor Dashboard</h1>
    </nav>

    <main>
        <h2>Live CAN Data</h2>
        <div class="controls">
            <input type="text" id="filter" placeholder="Filter by CAN ID..." />
            <button id="toggle">Pause</button>
            <button id="download">Download CSV</button>
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
                <!-- Data will be inserted here -->
            </tbody>
        </table>
    </main>

    <footer>
        &copy; 2025 CAN Monitor | Powered by Flask + Socket.IO
    </footer>

    <script>
        const socket = io();
        const log = document.getElementById("log");
        const filterInput = document.getElementById("filter");
        const toggleBtn = document.getElementById("toggle");
        const downloadBtn = document.getElementById("download");

        const maxRows = 100;
        let paused = false;
        let messages = [];

        socket.on("can_message", (data) => {
            if (paused) return;

            messages.unshift(data);
            if (messages.length > maxRows) messages = messages.slice(0, maxRows);
            renderTable();
        });

        function renderTable() {
            const filterValue = filterInput.value.trim().toLowerCase();
            log.innerHTML = "";

            for (const msg of messages) {
                if (!msg.id.toLowerCase().includes(filterValue)) continue;

                const row = document.createElement("tr");
                row.innerHTML = \`
                    <td>\${msg.id}</td>
                    <td>\${msg.data}</td>
                    <td>\${msg.timestamp}</td>
                \`;
                log.appendChild(row);
            }
        }

        filterInput.addEventListener("input", renderTable);

        toggleBtn.addEventListener("click", () => {
            paused = !paused;
            toggleBtn.textContent = paused ? "Resume" : "Pause";
        });

        downloadBtn.addEventListener("click", () => {
            if (messages.length === 0) return;

            let csv = "CAN ID,Data,Timestamp\\n";
            messages.forEach(msg => {
                csv += \`\${msg.id},\${msg.data},\${msg.timestamp}\\n\`;
            });

            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "can_data.csv";
            a.click();
            URL.revokeObjectURL(url);
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_template)

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
