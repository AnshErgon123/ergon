import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'server', 'templates'))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'password':
        return render_template('ok.html', username=username)
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/data')
def data():
    return render_template('data.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
