import os
from spotipy.oauth2 import SpotifyOAuth

auth_manager = SpotifyOAuth(
    scope="playlist-modify-public",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")
)

# This generates the clean web link
auth_url = auth_manager.get_authorize_url()
print("\n🔗 Copy and paste this exact link into your Brave Browser:")
print(auth_url)
