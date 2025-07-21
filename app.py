from flask import Flask, redirect, request, render_template, jsonify, session
import requests
import base64
import json
from urllib.parse import urlencode
from playlist_handler import SpotifyPlaylistManager

app = Flask(__name__)
app.secret_key = "markus"  # 🔐 notwendig für session (z. B. um Votes pro User zu speichern)

# 🔐 Spotify API-Zugang
CLIENT_ID = "365e83ace9494e878923a23b42305129"
CLIENT_SECRET = "262d86ab75174a609be1b27180faded3"
REDIRECT_URI = "https://spotify-voting-app.onrender.com/callback"
PLAYLIST_ID = "1FRH27WUto6I32gBRJNVYp"  # <== ERSETZEN!

# 📦 Lokale Datei zum Speichern der Votes
DATA_FILE = "data.json"

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"votes": {}}

# 💾 Access Token speichern (einfach für Demo-Zwecke)
ACCESS_TOKEN = ""

import time

def reset_all_votes():
    data = {"votes": {}, "user_votes": {}}
    save_data(data)

def reset_user_votes():
    data = load_data()
    data["user_votes"] = {}
    save_data(data)

def auto_reset_user_votes():
    data = load_data()
    now = time.time()
    last_reset = data.get("last_reset", 0)

    # Alle 600 Sekunden (10 Minuten)
    if now - last_reset > 600:
        print("🔁 Automatischer Reset der User-Votes")
        data["user_votes"] = {}
        data["last_reset"] = now
        save_data(data)


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
    auto_reset_user_votes()

    if not ACCESS_TOKEN:
        return redirect("/")
    spotify = SpotifyPlaylistManager(ACCESS_TOKEN, PLAYLIST_ID)
    tracks = spotify.get_playlist_tracks()

    # Votes laden
    data = load_data()
    votes = data["votes"]

    # Aktuellen Song zurücksetzen
    current = spotify.get_currently_playing()
    if current and current in votes:
        votes[current] = 0
        save_data(data)

    # Songs mit Votes kombinieren
    for song in tracks:
        song["votes"] = votes.get(song["id"], 0)

    # Sortieren nach Votes
    tracks.sort(key=lambda s: s["votes"], reverse=True)

    return render_template("voting.html", songs=tracks, playlist_cover_url="/static/Club_40.jpeg")


@app.route("/vote", methods=["POST"])
def vote():
    song_id = request.json.get("song_id")
    ip = request.remote_addr

    data = load_data()
    votes = data.get("votes", {})
    user_votes = data.get("user_votes", {})

    # Wenn IP schon für diesen Song gevotet hat → kein weiteres Voting
    if ip in user_votes and song_id in user_votes[ip]:
        return jsonify(success=False, message="WIE OFT DEN NOCH?")

    # Vote zählen
    votes[song_id] = votes.get(song_id, 0) + 1

    # IP merken
    if ip not in user_votes:
        user_votes[ip] = []
    user_votes[ip].append(song_id)

    # Speichern
    data["votes"] = votes
    data["user_votes"] = user_votes
    save_data(data)

    return jsonify(success=True, message="Gute Wahl!")



@app.route("/admin-reset-all")
def admin_reset_all():
    reset_all_votes()
    return "✅ Alle Votes & User-Daten wurden zurückgesetzt."

@app.route("/admin-reset-user-votes")
def admin_reset_users():
    reset_user_votes()
    return "✅ Nur User-Votes wurden zurückgesetzt. Stimmen bleiben erhalten."
