from flask import Flask, render_template_string, jsonify, request, abort
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app)

connected = False
message_count = 0

SECRET_TOKEN = os.getenv("SECRET_TOKEN", "default-token")

HTML_PAGE = ''' 
<!-- Keep your existing HTML here (unchanged) -->
<!-- This is the full HTML_PAGE string from your original code -->
'''  # use your full HTML_PAGE here

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/status')
def status():
    return jsonify({'connected': connected, 'message_count': message_count})

@app.route('/api/send_data', methods=['POST'])
def receive_data():
    global message_count
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {SECRET_TOKEN}":
        abort(403)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400

    message_count += 1
    socketio.emit('can_message', {
        'timestamp': data['timestamp'],
        'id': data['id'],
        'data': data['data']
    })

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5050)
