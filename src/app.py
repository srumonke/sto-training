import os
import sqlite3
import yaml
import subprocess
from flask import Flask, request, render_template_string, redirect, session, make_response

import config

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key-12345"

# -------------------------------------------------------
# Database setup
# -------------------------------------------------------
def get_db():
    db = sqlite3.connect("app.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT
        )
    """)
    return db


# -------------------------------------------------------
# SAST: SQL Injection - user input concatenated into query
# -------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
        user = db.execute(query).fetchone()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[4]
            return redirect("/dashboard")
        return "Login failed", 401

    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
    """)


# -------------------------------------------------------
# SAST: Reflected XSS - user input rendered without escaping
# -------------------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("q", "")
    return render_template_string("<h2>Results for: " + query + "</h2><p>No results found.</p>")


# -------------------------------------------------------
# SAST: Command Injection - user input passed to shell
# -------------------------------------------------------
@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    result = subprocess.check_output("ping -c 1 " + host, shell=True)
    return "<pre>" + result.decode() + "</pre>"


# -------------------------------------------------------
# SAST: Insecure deserialization - loading untrusted YAML
# -------------------------------------------------------
@app.route("/import", methods=["POST"])
def import_data():
    raw = request.form.get("data", "")
    data = yaml.load(raw)
    return "Imported: " + str(data)


# -------------------------------------------------------
# SAST: Path traversal - user controls file path
# -------------------------------------------------------
@app.route("/file")
def read_file():
    filename = request.args.get("name", "")
    filepath = os.path.join("/app/data", filename)
    with open(filepath, "r") as f:
        content = f.read()
    return "<pre>" + content + "</pre>"


# -------------------------------------------------------
# SAST: Hardcoded credentials in code
# -------------------------------------------------------
@app.route("/admin")
def admin():
    admin_password = "admin123"
    provided = request.args.get("password", "")
    if provided == admin_password:
        return "Welcome, admin!"
    return "Access denied", 403


# -------------------------------------------------------
# Code Quality: Unused variables, dead code, complexity
# -------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    unused_var = "this is never used"
    temp = 42
    x = None
    y = None
    z = None

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    db = get_db()
    notes = db.execute("SELECT * FROM notes WHERE user_id=?", (user_id,)).fetchall()

    html = "<h2>Dashboard</h2>"
    for note in notes:
        html += "<div><b>" + str(note[2]) + "</b><p>" + str(note[3]) + "</p></div>"
    return html


# -------------------------------------------------------
# SAST: Insecure cookie settings
# -------------------------------------------------------
@app.route("/set-cookie")
def set_cookie():
    resp = make_response("Cookie set")
    resp.set_cookie("session_token", "abc123", httponly=False, secure=False, samesite=None)
    return resp


# -------------------------------------------------------
# SAST: Open redirect
# -------------------------------------------------------
@app.route("/redirect")
def open_redirect():
    url = request.args.get("url", "/")
    return redirect(url)


# -------------------------------------------------------
# DAST: Weak headers - no security headers set
# -------------------------------------------------------
@app.route("/")
def home():
    return """
    <html>
    <head><title>Hub24 STO Demo</title></head>
    <body>
        <h1>Hub24 STO Training App</h1>
        <ul>
            <li><a href="/login">Login</a></li>
            <li><a href="/search?q=test">Search</a></li>
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href="/admin?password=test">Admin</a></li>
        </ul>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
