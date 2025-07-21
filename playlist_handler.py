import requests
import json

class SpotifyPlaylistManager:
    def __init__(self, token, playlist_id):
        self.token = token
        self.playlist_id = playlist_id
        self.api_url = "https://api.spotify.com/v1"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

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

        except Exception as e:
            print("❌ Ausnahme beim Abrufen der Playlist:", str(e))
            return []

    def get_playlist_cover(self):
        url = f"{self.api_url}/playlists/{self.playlist_id}"
        headers = self.get_headers()

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["images"][0]["url"]
        except Exception as e:
            print("❌ Fehler beim Laden des Covers:", str(e))
            return None
