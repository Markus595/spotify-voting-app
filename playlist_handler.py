import requests

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
        res.raise_for_status()
        items = res.json()["items"]
        return [
            {
                "id": item["track"]["id"],
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"]
            }
            for item in items
        ]

    def get_currently_playing(self):
        url = f"{self.api_url}/me/player/currently-playing"
        res = requests.get(url, headers=self.get_headers())
        if res.status_code == 204:
            return None
        res.raise_for_status()
        data = res.json()
        return data["item"]["id"]
