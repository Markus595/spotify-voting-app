from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", songs=data["votes"])

@app.route("/vote", methods=["POST"])
def vote():
    song_id = request.json.get("song_id")
    data = load_data()
    if song_id in data["votes"]:
        data["votes"][song_id] += 1
    else:
        data["votes"][song_id] = 1
    save_data(data)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)