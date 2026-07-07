import os
import json
import streamlit as st
from groq import Groq
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="AI YouTube Playlist Builder", page_icon="🎵")
st.title("🎵 AI YouTube Playlist Builder")

# 1. Base API Authentication Configurations
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google"]["client_id"],
        "client_secret": st.secrets["google"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

# Initialize a persistent backend memory state
if "youtube_creds" not in st.session_state:
    st.session_state.youtube_creds = None

# 2. Check Browser URL bar for incoming Google Redirect tokens
query_params = st.query_params
if "code" in query_params and not st.session_state.youtube_creds:
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=REDIRECT_URI)
        flow.code_verifier = st.session_state.get("code_verifier")  # restore PKCE verifier
        flow.fetch_token(code=query_params["code"])
        st.session_state.youtube_creds = flow.credentials
        st.query_params.clear()  # Clean up the browser address bar string
        st.rerun()
    except Exception as e:
        st.error(f"Handshake validation error: {e}")
        st.stop()

# 3. UI Gateway: Lock app until authentication succeeds
if not st.session_state.youtube_creds:
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    st.session_state.code_verifier = flow.code_verifier  # save PKCE verifier for the callback
    
    st.markdown("### 🔐 Google Account Authorization Required")
    st.write("Connect your profile to allow the cloud server to create custom music playlists directly on your account.")
    st.markdown(f'### 🔗 [Click here to securely authorize your YouTube Account]({auth_url})')
    st.stop()

# 4. Initialize API Core Clients if Login token is active
groq_client = Groq()
youtube_client = build('youtube', 'v3', credentials=st.session_state.youtube_creds)

st.success("🔒 Secured Cloud Google/YouTube Engine Connected Successfully!")

# --- Core App Playlist Curation UI Dashboard ---
user_prompt = st.text_input("What kind of playlist do you want to create?", "Make a high energy songs playlist with songs from charli xcx and kim petras")
generate_button = st.button("Build Single Playlist Link 🚀")

if generate_button:
    with st.spinner("🤖 AI is curating songs..."):
        ai_response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a music curator. Respond ONLY with a valid JSON array of objects with 'artist' and 'track' keys. No explanations."
                },
                {"role": "user", "content": user_prompt}
            ]
        )
        try:
            songs_to_find = json.loads(ai_response.choices[0].message.content.strip())
        except Exception:
            st.error("AI parsing error. Click the button to try again.")
            st.stop()

    with st.spinner("🎵 Creating playlist on your YouTube channel..."):
        playlist_response = youtube_client.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": f"AI: {user_prompt[:30]}",
                    "description": "Generated instantly by my custom AI Python web app interface framework."
                },
                "status": {"privacyStatus": "public"}
            }
        ).execute()
        playlist_id = playlist_response["id"]

    with st.spinner("⚡ Finding tracks and injecting them..."):
        for song in songs_to_find:
            search_query = f"{song['artist']} - {song['track']} topic"
            search_res = youtube_client.search().list(q=search_query, part="id", maxResults=1, type="video", videoCategoryId="10").execute()
            items = search_res.get("items", [])
            
            if items:
                video_id = items[0]["id"]["videoId"]
                youtube_client.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": video_id}
                        }
                    }
                ).execute()

    st.success("🎉 Playlist build execution complete!")
    playlist_url = f"https://youtube.com/playlist?list={playlist_id}"
    st.markdown(f"### 🔗 [Click here to open the entire playlist directly in YouTube]({playlist_url})")
