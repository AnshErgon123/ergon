from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
import os, time

app = Flask(__name__)
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
    /* ... your existing styles ... */
    nav .status { /* red by default */ background-color: #c62828; }
    nav .status.connected { background-color: #2e7d32; }
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
      <thead><tr><th>CAN ID</th><th>Data</th><th>Timestamp</th></tr></thead>
      <tbody id="log"></tbody>
    </table>
  </main>
  <footer>CAN Monitor | by Ergon Mobility</footer>

  <script>
    const socket = io();
    const statusEl    = document.getElementById("status");
    const log         = document.getElementById("log");
    const searchInput = document.getElementById("searchInput");
    let allMsgs = [], heartbeatTimer;

    // CAN data arrives here
    socket.on("can_message", data => {
      allMsgs.unshift(data);
      if (allMsgs.length > 100) allMsgs.pop();
      renderTable();
    });

    // Heartbeat carries real status from client.py
    socket.on("heartbeat", payload => {
      const st = payload.status === "online" ? "Connected" : "Disconnected";
      setStatus(st);
      // If online, reset timer; if offline, immediate UI change
      clearTimeout(heartbeatTimer);
      if (payload.status === "online") {
        heartbeatTimer = setTimeout(() => setStatus("Disconnected"), 5000);
      }
    });

    function setStatus(text) {
      statusEl.textContent = text;
      statusEl.classList.toggle("connected", text === "Connected");
    }

    searchInput.addEventListener("input", renderTable);

    function renderTable() {
      const f = searchInput.value.toLowerCase();
      log.innerHTML = "";
      for (const msg of allMsgs.filter(m =>
        m.id.toLowerCase().includes(f) ||
        m.data.toLowerCase().includes(f)
      )) {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${msg.id}</td><td>${msg.data}</td><td>${msg.timestamp}</td>`;
        log.appendChild(row);
      }
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
    # Broadcast real client status
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
