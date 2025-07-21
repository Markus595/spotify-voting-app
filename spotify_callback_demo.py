from flask import Flask, redirect, request
import spotify_auth

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(spotify_auth.get_auth_url())

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = spotify_auth.get_token(code)
    return f"<h1>Access Token:</h1><p>{token_info}</p>"

if __name__ == "__main__":
    app.run(debug=True)

# Trigger redeploy
