from flask import Flask, render_template_string, jsonify, request, abort, url_for
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # CORS enabled for local client

connected = False
message_count = 0

# HTML page
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ERGON - CAN Monitor</title>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; }
    header { background-color: #000; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
    header h1 { margin: 0; font-size: 24px; }
    header img { height: 40px; }
    .container { padding: 30px; max-width: 1000px; margin: auto; }
    .status { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .connected { color: green; }
    .disconnected { color: red; }
    #total { font-size: 16px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; }
    th, td { padding: 10px; border: 1px solid #ddd; text-align: center; }
    th { background-color: #003366; color: white; }
    tbody tr:nth-child(odd) { background: #f9f9f9; }
    tbody tr:hover { background: #e2f0ff; }
  </style>
</head>
<body>
  <header>
    <h1>ERGON - CAN Monitor</h1>
    <img src="{{ url_for('static', filename='download.png') }}" alt="ERGON Logo">
  </header>
  <div class="container">
    <div class="status">Status: <span id="status-text" class="disconnected">Disconnected</span></div>
    <div id="total">Total Messages: <span id="message-count">0</span></div>
    <table>
      <thead>
        <tr><th>Timestamp</th><th>ID</th><th>Data</th></tr>
      </thead>
      <tbody id="data-table"></tbody>
    </table>
  </div>
  <script>
    const socket = io();
    const statusText = document.getElementById('status-text');
    const countEl = document.getElementById('message-count');
    const tableBody = document.getElementById('data-table');
    let count = 0;

    function updateStatus(isConnected) {
      statusText.textContent = isConnected ? 'Connected' : 'Disconnected';
      statusText.className = isConnected ? 'connected' : 'disconnected';
    }

    fetch('/status')
      .then(res => res.json())
      .then(data => updateStatus(data.connected));

    socket.on('can_message', msg => {
      const row = tableBody.insertRow(-1);
      row.insertCell(0).textContent = new Date(msg.timestamp * 1000).toLocaleTimeString();
      row.insertCell(1).textContent = "0x" + msg.id.toString(16).toUpperCase();
      row.insertCell(2).textContent = msg.data;
      count++;
      countEl.textContent = count;
    });

    socket.on('status_update', data => {
      updateStatus(data.connected);
    });
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/status')
def status():
    return jsonify({'connected': connected, 'message_count': message_count})

# POST endpoint for client to send CAN data
@app.route('/api/send_data', methods=['POST'])
def receive_can_data():
    global connected, message_count

    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip()

    # Validate token
    if token != os.getenv('SECRET_TOKEN'):
        print("🔒 Invalid token received")
        abort(401)

    data = request.get_json()
    if not data:
        return 'Bad request', 400

    connected = True
    message_count += 1

    # Broadcast to front-end via socket
    socketio.emit('can_message', data)
    socketio.emit('status_update', {'connected': True})

    print(f"📨 Received: {data}")
    return 'OK', 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5050)
