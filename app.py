from flask import Flask, redirect, request, jsonify
import requests
import base64
from urllib.parse import urlencode

app = Flask(__name__)

# Spotify API credentials (aus deinem Dashboard)
CLIENT_ID = "365e83ace9494e878923a23b42305129"
CLIENT_SECRET = "262d86ab75174a609be1b27180faded3"
REDIRECT_URI = "https://spotify-voting-app.onrender.com/callback"

# Scopes: Diese brauchst du
SCOPES = "playlist-modify-public playlist-read-private user-read-currently-playing"

@app.route("/")
def index():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
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
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    token_url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        return f"Failed to get token: {response.text}", 400

    token_info = response.json()
    return jsonify(token_info)
