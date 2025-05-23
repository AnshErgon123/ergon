import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        return "Invalid credentials", 401

@app.route("/dashboard")
def dashboard():
    return "Welcome to your dashboard!"

# ✅ Use PORT from environment (for Render.com)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 for local testing
    app.run(host="0.0.0.0", port=port, debug=True)
