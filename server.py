from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from flask_socketio import SocketIO
import os, time, csv
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # You can add real authentication here
        return redirect(url_for('data'))
    return render_template("login.html", title="Login")

@app.route("/data")
def data():
    return render_template("data.html", title="CAN Data")

@app.route("/ok")
def ok():
    return render_template("ok.html", title="OK Page")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # default to 10000 for local dev
    socketio.run(app, host="0.0.0.0", port=port)
