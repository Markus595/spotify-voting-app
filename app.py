from flask import Flask, redirect, request, render_template, jsonify, session, flash
import requests
import base64
import json
from urllib.parse import urlencode
from playlist_handler import SpotifyPlaylistManager
import os

app = Flask(__name__)
app.secret_key = "markus"  # Admin-Zugang absichern

# 🔐 Spotify API-Zugang
CLIENT_ID = "365e83ace9494e878923a23b42305129"
CLIENT_SECRET = "262d86ab75174a609be1b27180faded3"
REDIRECT_URI = "https://spotify-voting-app.onrender.com/callback"
PLAYLIST_ID = "1FRH27WUto6I32gBRJNVYp"

# 📁 Daten-Datei
DATA_FILE = "data.json"

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"votes": {}, "user_votes": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# 💾 Access Token
ACCESS_TOKEN = ""

@app.route("/")
def index():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "playlist-read-private user-read-currently-playing"
    })
    auth_url = f"https://accounts.spotify.com/authorize?{query}"
    return f"""
        <h2>Vote for the next song!</h2>
        <a href="{auth_url}">
            <button style='font-size:20px;padding:10px 20px;'>Login with Spotify</button>
        </a>
    """

@app.route("/callback")
def callback():
    global ACCESS_TOKEN
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        return f"Token error: {response.text}"
    ACCESS_TOKEN = response.json()["access_token"]
    return redirect("/vote")

@app.route("/vote")
def vote_page():
    if not ACCESS_TOKEN:
        return redirect("/")
    spotify = SpotifyPlaylistManager(ACCESS_TOKEN, PLAYLIST_ID)
    tracks = spotify.get_playlist_tracks()

    data = load_data()
    votes = data["votes"]
    user_votes = data.get("user_votes", {})
    user_id = request.remote_addr

    current = spotify.get_currently_playing()
      if current and current in votes:
        votes[current] = 0
        data["votes"] = votes
        save_data(data)



    for song in tracks:
        song["votes"] = votes.get(song["id"], 0)
        song["already_voted"] = song["id"] in user_votes.get(user_id, [])

    tracks.sort(key=lambda s: s["votes"], reverse=True)

    return render_template("voting.html", songs=tracks)

@app.route("/vote", methods=["POST"])
def vote():
    song_id = request.json.get("song_id")
    user_id = request.remote_addr

    data = load_data()
    votes = data["votes"]
    user_votes = data.get("user_votes", {})

    if user_id not in user_votes:
        user_votes[user_id] = []

    if song_id in user_votes[user_id]:
        return jsonify(success=False, message="WIE OFT DEN NOCH?")
    else:
        votes[song_id] = votes.get(song_id, 0) + 1
        user_votes[user_id].append(song_id)
        save_data({"votes": votes, "user_votes": user_votes})
        return jsonify(success=True, message="Gute Wahl!")

# ===================== 🔐 Admin Bereich ======================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "markus":
            session["is_admin"] = True
            return redirect("/admin-panel")
        else:
            return render_template("admin_login.html", error="❌ Falsches Passwort.")
    return render_template("admin_login.html")

@app.route("/admin-panel")
def admin_panel():
    if not session.get("is_admin"):
        return redirect("/admin")
    return render_template("admin_panel.html")

@app.route("/admin-reset-all")
def reset_all():
    if not session.get("is_admin"):
        return redirect("/admin")
    save_data({"votes": {}, "user_votes": {}})
    flash("✅ Alle Votes + User-Votes wurden zurückgesetzt.")
    return redirect("/admin-panel")

@app.route("/admin-reset-user-votes")
def reset_user_votes():
    if not session.get("is_admin"):
        return redirect("/admin")
    data = load_data()
    data["user_votes"] = {}
    save_data(data)
    flash("✅ Nur User-Votes wurden zurückgesetzt.")
    return redirect("/admin-panel")
