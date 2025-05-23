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
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Bootstrap 5 -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
  <style>
    body { padding-top: 70px; }
    .status-dot {
      display: inline-block;
      width: .75rem; height: .75rem;
      border-radius: 50%;
      margin-right: .5rem;
      background-color: #dc3545;
    }
    .status-dot.online { background-color: #28a745; }
    footer {
      background: #f8f9fa;
      padding: 1rem 0;
      position: fixed;
      bottom: 0;
      width: 100%;
      text-align: center;
      border-top: 1px solid #e4e4e4;
    }
    table tbody tr:nth-child(even) { background-color: #f8f9fa; }
    .table-wrapper { max-height: 60vh; overflow-y: auto; }
  </style>
</head>
<body>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top shadow-sm">
    <div class="container-fluid">
      <a class="navbar-brand d-flex align-items-center" href="#">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" width="30" height="30" class="d-inline-block align-text-top">
        <span class="ms-2">CAN Monitor</span>
      </a>
      <div class="d-flex">
        <div id="status-indicator" class="status-dot"></div>
        <span id="status-text">Disconnected</span>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="container my-4">
    <div class="row mb-3">
      <div class="col-md-6">
        <input id="searchInput" type="text" class="form-control" placeholder="Filter by CAN ID or Data...">
      </div>
    </div>
    <div class="table-wrapper">
      <table class="table table-striped table-bordered">
        <thead class="table-primary">
          <tr>
            <th>CAN ID</th>
            <th>Data</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody id="log"></tbody>
      </table>
    </div>
  </main>

  <!-- Footer -->
  <footer>
    <div class="container">
      <small class="text-muted">© 2025 Ergon Mobility · Live CAN Bus Dashboard</small>
    </div>
  </footer>

  <!-- Socket.IO + JS Logic -->
  <script>
    const socket      = io();
    const log         = document.getElementById("log");
    const searchInput = document.getElementById("searchInput");
    const dot         = document.getElementById("status-indicator");
    const text        = document.getElementById("status-text");
    let allMsgs = [], heartbeatTimer;

    socket.on("can_message", data => {
      allMsgs.unshift(data);
      if (allMsgs.length > 100) allMsgs.pop();
      renderTable();
    });

    socket.on("heartbeat", payload => {
      const isOnline = payload.status === "online";
      setStatus(isOnline);
      clearTimeout(heartbeatTimer);
      if (isOnline) {
        heartbeatTimer = setTimeout(() => setStatus(false), 5000);
      }
    });

    function setStatus(online) {
      dot.classList.toggle("online", online);
      text.textContent = online ? "Connected" : "Disconnected";
    }

    searchInput.addEventListener("input", renderTable);

    function renderTable() {
      const filter = searchInput.value.toLowerCase();
      log.innerHTML = "";
      allMsgs.filter(m =>
        m.id.toLowerCase().includes(filter) ||
        m.data.toLowerCase().includes(filter)
      ).forEach(msg => {
        const row = document.createElement("tr");
        row.innerHTML = 
          <td>${msg.id}</td>
          <td>${msg.data}</td>
          <td>${msg.timestamp}</td>
        ;
        log.appendChild(row);
      });
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