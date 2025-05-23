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
  <meta charset="UTF-8" />
  <title>CAN Bus Live Monitor</title>
  <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
  <style>
    /* ... your existing styles here ... */
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
        <tr><th>CAN ID</th><th>Data</th><th>Timestamp</th></tr>
      </thead>
      <tbody id="log"></tbody>
    </table>
  </main>

  <footer>
    &copy; 2025 CAN Monitor | Powered by Flask + Socket.IO
  </footer>

  <script>
    // connect explicitly back to this origin
    const socket = io(window.location.origin);
    console.log("⚡ Attempting Socket.IO connection…");

    socket.on("connect", () => {
      console.log("✅ Socket connected, id =", socket.id);
    });
    socket.on("disconnect", () => {
      console.log("🛑 Socket disconnected");
    });

    const log = document.getElementById("log");
    const filterInput = document.getElementById("filter");
    const toggleBtn = document.getElementById("toggle");
    const downloadBtn = document.getElementById("download");

    const maxRows = 100;
    let paused = false;
    let messages = [];

    socket.on("can_message", (data) => {
      console.log("📥 Received:", data);
      if (paused) return;
      messages.unshift(data);
      if (messages.length > maxRows) messages.length = maxRows;
      renderTable();
    });

    function renderTable() {
      const filterValue = String(filterInput.value).trim().toLowerCase();
      log.innerHTML = "";
      for (const msg of messages) {
        const idStr = String(msg.id).toLowerCase();
        if (filterValue && !idStr.includes(filterValue)) continue;
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${msg.id}</td>
          <td>${msg.data}</td>
          <td>${msg.timestamp}</td>
        `;
        log.appendChild(row);
      }
    }

    filterInput.addEventListener("input", renderTable);

    toggleBtn.addEventListener("click", () => {
      paused = !paused;
      toggleBtn.textContent = paused ? "Resume" : "Pause";
    });

    downloadBtn.addEventListener("click", () => {
      if (!messages.length) return;
      let csv = "CAN ID,Data,Timestamp\n";
      messages.forEach(m => {
        csv += `${m.id},${m.data},${m.timestamp}\n`;
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
