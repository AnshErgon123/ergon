from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route to display login form (GET request)
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

# Route to handle login submission (POST request)
@app.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    # Dummy authentication logic (replace with real validation)
    if username == "admin" and password == "admin":
        return redirect(url_for("dashboard"))
    else:
        return "Invalid credentials", 401

# Optional: Dashboard route after successful login
@app.route("/dashboard")
def dashboard():
    return "Welcome to your dashboard!"

if __name__ == "__main__":
    app.run(debug=True)
