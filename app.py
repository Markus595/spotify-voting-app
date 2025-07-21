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

    # Stelle sicher, dass session läuft
    if "voted_songs" not in session:
        session["voted_songs"] = []

    # Prüfe, ob schon gevotet wurde
    if song_id in session["voted_songs"]:
        return jsonify(success=False, message="WIE OFT DENN NOCH?!")

    # Stimme speichern
    data = load_data()
    votes = data["votes"]
    if song_id in votes:
        votes[song_id] += 1
    else:
        votes[song_id] = 1
    save_data(data)

    # Song-ID in Session eintragen
    session["voted_songs"].append(song_id)
    session.modified = True

    return jsonify(success=True)
