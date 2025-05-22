import os, time, csv, json
from datetime import datetime
from flask import (
    Flask, request, jsonify,
    render_template, send_file
)
from flask_socketio import SocketIO

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
socketio = SocketIO(app, cors_allowed_origins="*")

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")
CSV_FILE      = "can_log.csv"
SCHEMA_FILE   = "schema.json"

# Create CSV if missing
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp","can_id","data"])

def load_schema():
    with open(SCHEMA_FILE) as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/parameters")
def parameters():
    schema = load_schema()
    columns = list(schema[0].keys()) if schema else []
    return render_template(
        "parameters.html",
        schema=schema,
        columns=columns
    )

@app.route("/api/schema")
def api_schema():
    return jsonify(load_schema())

@app.route("/api/send_data", methods=["POST"])
def receive_data():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer ") or auth.split()[1] != SECRET_TOKEN:
        return jsonify({"error":"Unauthorized"}), 401

    data     = request.get_json() or {}
    can_id   = data.get("id","")
    can_data = data.get("data","")
    ts       = data.get("timestamp") or datetime.utcnow().isoformat()

    socketio.emit("can_message", {
        "id":        can_id,
        "data":      can_data,
        "timestamp": ts
    })

    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([ts, can_id, can_data])

    return jsonify({"status":"received"}), 200

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer ") or auth.split()[1] != SECRET_TOKEN:
        return jsonify({"error":"Unauthorized"}), 401

    status = (request.get_json() or {}).get("status","offline")
    socketio.emit("heartbeat", {"status": status, "ts": time.time()})
    return jsonify({"status":"ok"}), 200

@app.route("/logs/download")
def download_logs():
    return send_file(CSV_FILE, as_attachment=True)

@socketio.on("connect")
def on_connect():
    print("Web client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Web client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
