from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

SECRET_TOKEN = os.getenv("SECRET_TOKEN", "supersecret")

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>CAN Dashboard</title>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
  <h1>CAN Dashboard</h1>
  <div>Status: <span id="status">Disconnected</span></div>
  <div>Total Messages: <span id="count">0</span></div>
  <table border="1">
    <thead>
      <tr><th>Time</th><th>ID</th><th>Data</th></tr>
    </thead>
    <tbody id="messages"></tbody>
  </table>

  <script>
    const socket = io();
    let count = 0;
    socket.on('can_message', data => {
      document.getElementById('status').innerText = 'Connected';
      count += 1;
      document.getElementById('count').innerText = count;
      const row = document.createElement('tr');
      row.innerHTML = `<td>${new Date(data.timestamp * 1000).toLocaleTimeString()}</td><td>0x${data.id.toString(16).toUpperCase()}</td><td>${data.data}</td>`;
      document.getElementById('messages').appendChild(row);
    });
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/send_data', methods=['POST'])
def receive_data():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    socketio.emit("can_message", data)
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050)
