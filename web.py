from flask import Flask, request, redirect, jsonify
from instagrapi import Client
import os

app = Flask(__name__)
cl = Client()
SESSION_PATH = "session/session.json"

@app.route("/")
def home():
    return '<h2>Instagram botga kirish</h2><a href="/login">Login</a>'

@app.route("/login")
def login():
    return '<h3>Instagram sahifasiga kiring:</h3><a href="https://www.instagram.com/accounts/login/">Login</a>'

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    try:
        cl.login(username, password)
        cl.dump_settings(SESSION_PATH)  # Sessiyani saqlash
        return jsonify({"status": "success", "message": "✅ Instagram login bo‘ldi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/session_status")
def session_status():
    try:
        cl.load_settings(SESSION_PATH)
        if cl.user_id:
            return jsonify({"status": "success", "message": "🔵 Sessiya faol"})
        else:
            return jsonify({"status": "error", "message": "🔴 Sessiya yo‘q"})
    except:
        return jsonify({"status": "error", "message": "🔴 Sessiya mavjud emas"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
