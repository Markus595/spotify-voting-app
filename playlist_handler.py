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
        res = requests.get(url, headers=self.get_headers())

        try:
            res.raise_for_status()
            data = res.json()

            if "items" not in data:
                print("❌ Fehler: 'items' nicht in Antwort von Spotify.")
                print(json.dumps(data, indent=2))
                return []

            items = data["items"]

            # Songs extrahieren
            return [
                {
                    "id": item["track"]["id"],
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"]
                }
                for item in items
                if item.get("track") and item["track"].get("id")
            ]

        except Exception as e:
            print("❌ Ausnahme beim Abrufen der Playlist:", str(e))
            return []

