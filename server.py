import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecret')  # Change this in production
CORS(app)

@app.route("/")
def index():
    return redirect(url_for("login_form"))

@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "admin":
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid credentials")
        return "Invalid credentials", 401

@app.route("/dashboard")
def dashboard():
    return "Welcome to your dashboard!"

# Production server configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
