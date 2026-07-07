import os
import json
import streamlit as st
from groq import Groq
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="AI YouTube Playlist Builder", page_icon="🎵")
st.title("🎵 AI YouTube Playlist Builder")

# 1. Native Streamlit User Auth Check
if not st.user.is_logged_in:
    st.markdown("### 🔐 Google Account Authorization Required")
    st.write("Connect your account to allow the app to securely publish playlists to your YouTube channel.")
    if st.button("Log in with Google 🚀"):
        st.login() # Triggers native, seamless browser popup wrapper
    st.stop()

# 2. Extract Auth Tokens from the logged-in user profile
user_token = st.user.auth_token

# Build credentials object to feed directly into the Google/YouTube client
creds = Credentials(token=user_token)

# Initialize engines cleanly
groq_client = Groq()
youtube_client = build('youtube', 'v3', credentials=creds)

st.success(f"🔒 Welcome {st.user.name}! Connected to YouTube Channel successfully!")

if st.button("Log out"):
    st.logout()
    st.rerun()

# --- Core App UI Generation Dashboard ---
user_prompt = st.text_input("What kind of playlist do you want to create?", "Make a high energy songs playlist with songs from charli xcx and kim petras")
generate_button = st.button("Build Single Playlist Link 🚀")

if generate_button:
    with st.spinner("🤖 AI is curating tracks..."):
        ai_response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
            st.error("AI formatting parsing error. Please click button again to regenerate.")
            st.stop()

    # 1. Create playlist container on your YouTube Account
    with st.spinner("🎵 Creating fresh playlist container on your YouTube account..."):
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

    # 2. Extract song catalog matches and inject them directly into your new container
    with st.spinner("⚡ Processing matches and injecting audio files..."):
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

    # 3. Present the single compiled shareable link
    st.success("🎉 Compilation processing complete! Your playlist is ready.")
    playlist_url = f"https://youtube.com{playlist_id}"
    st.markdown(f"### 🔗 [Click here to open the entire playlist directly in YouTube]({playlist_url})")

