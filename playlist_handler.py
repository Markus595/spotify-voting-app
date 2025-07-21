import requests
import json

class SpotifyPlaylistManager:
    def __init__(self, access_token, playlist_id):
        self.token = access_token
        self.playlist_id = playlist_id
        self.api_url = "https://api.spotify.com/v1"

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_playlist_tracks(self):
        url = f"{self.api_url}/playlists/{self.playlist_id}/tracks"
        headers = self.get_headers()
        print("📡 Anfrage an:", url)
        print("🔐 Header:", headers)

        try:
            res = requests.get(url, headers=headers)
            print("📥 Antwort:", res.status_code)
            data = res.json()
            print("📄 Antwortinhalt:")
            print(json.dumps(data, indent=2))

            if "items" not in data:
                print("❌ 'items' nicht enthalten!")
                return []

            items = data["items"]

            return [
                {
                    "id": item["track"]["id"],
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "image": item["track"]["album"]["images"][0]["url"]
                }
                for item in items
                if item.get("track") and item["track"].get("id")
            ]
def get_currently_playing(self):
    url = f"{self.api_url}/me/player/currently-playing"
    headers = self.get_headers()
    res = requests.get(url, headers=headers)
    
    if res.status_code == 204:
        return None  # Nothing is playing

    try:
        res.raise_for_status()
        data = res.json()
        return data["item"]["id"]
    except Exception as e:
        print("❌ Fehler beim Abrufen des aktuellen Songs:", str(e))
        return None

        except Exception as e:
            print("❌ Ausnahme beim Abrufen der Playlist:", str(e))
            return []
