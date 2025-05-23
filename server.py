from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CAN Bus Dashboard</title>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <style>
    body { font-family: sans-serif; padding: 1em; }
    .status-dot {
      height: 12px; width: 12px; border-radius: 50%;
      display: inline-block; margin-right: 5px;
    }
    .online { background: green; }
    .offline { background: red; }
    table { width: 100%; border-collapse: collapse; margin-top: 1em; }
    th, td { padding: 0.5em; border: 1px solid #ccc; text-align: left; }
  </style>
</head>
<body>
  <h2>CAN Bus Dashboard</h2>
  <p>
    <span id="statusDot" class="status-dot offline"></span>
    <span id="statusText">Disconnected</span>
  </p>
  <table>
    <thead>
      <tr><th>ID</th><th>Data</th><th>Timestamp</th></tr>
    </thead>
    <tbody id="log"></tbody>
  </table>

  <script>
    const socket = io();
    const log = document.getElementById("log");
    const statusDot = document.getElementById("statusDot");
    const statusText = document.getElementById("statusText");
    const allMsgs = [];

    function setStatus(isOnline) {
      statusDot.className = "status-dot " + (isOnline ? "online" : "offline");
      statusText.textContent = isOnline ? "Connected" : "Disconnected";
    }

    function renderTable() {
      log.innerHTML = "";
      allMsgs.forEach(msg => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${msg.id}</td>
          <td>${msg.data}</td>
          <td>${msg.timestamp}</td>
        `;
        log.appendChild(row);
      });
    }

    socket.on("connect", () => console.log("Socket.IO connected"));

    socket.on("can_message", msg => {
      allMsgs.push(msg);
      renderTable();
    });

    socket.on("heartbeat", payload => {
      const isOnline = payload.status === "online";
      setStatus(isOnline);
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(HTML_CONTENT, mimetype="text/html")

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json() or {}
    status = data.get("status", "offline")
    socketio.emit("heartbeat", {"status": status})
    return jsonify({"message": "Heartbeat received", "status": status})

@app.route("/api/can", methods=["POST"])
def receive_can():
    data = request.get_json() or {}
    socketio.emit("can_message", data)
    return jsonify({"message": "CAN message received"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
