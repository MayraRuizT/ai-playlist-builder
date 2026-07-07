import os
import json
import streamlit as st
from groq import Groq
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="AI YouTube Playlist Builder", page_icon="🎵")
st.title("🎵 AI YouTube Playlist Builder")

# Cloud Native Google OAuth Config
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google"]["client_id"],
        "client_secret": st.secrets["google"]["client_secret"],
        "auth_uri": "https://google.com",
        "token_uri": "https://googleapis.com",
    }
}
SCOPES = ['https://googleapis.com']

# Initialize session state for login credentials
if "google_creds" not in st.session_state:
    st.session_state.google_creds = None

# Checking Query Parameters for Login Code from Google
query_params = st.query_params
if "code" in query_params and not st.session_state.google_creds:
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=st.secrets["google"]["redirect_uri"])
    flow.fetch_token(code=query_params["code"])
    st.session_state.google_creds = flow.credentials
    # Clear the code from the URL for a cleaner layout look
    st.query_params.clear()

# Core Authentication Branch
if not st.session_state.google_creds:
    # This explicit initialization forces the correct browser redirection protocol
    flow = Flow.from_client_config(
        CLIENT_CONFIG, 
        scopes=SCOPES, 
        redirect_uri=st.secrets["google"]["redirect_uri"]
    )
    
    # Adding access_type='offline' and include_granted_scopes='true' forces the permission popup to appear
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    st.markdown("### 🔐 Google Account Authorization Required")
    st.markdown(f"[🔗 Click here to securely connect your YouTube Account]({auth_url})")
    st.stop()

# If authenticated, build your service clients seamlessly
groq_client = Groq()
youtube_client = build('youtube', 'v3', credentials=st.session_state.google_creds)

st.success("🔒 Secured Cloud Google/YouTube Engine Connected Successfully!")


user_prompt = st.text_input("What kind of playlist do you want to create?", "Make a high energy songs playlist with songs from charli xcx and kim petras")
generate_button = st.button("Build Single Playlist Link 🚀")

# All music code must sit indented inside this execution button check
if generate_button:
    with st.spinner("🤖 AI is curating tracks..."):
        ai_response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a music curator. Respond ONLY with a valid raw JSON array of objects with 'artist' and 'track' keys. Do not include markdown code blocks, do not use ```json wrappers, and do not write introductory text. Output raw JSON text only."
                },
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Clean up the output string to strip out common markdown fluff
        raw_output = ai_response.choices[0].message.content.strip()
        
        # This removes ```json or ``` if the AI accidentally adds them anyway
        if raw_output.startswith("```"):
            lines = raw_output.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_output = "\n".join(lines).strip()
            
        try:
            songs_to_find = json.loads(raw_output)
        except Exception as e:
            st.error(f"AI data format error. Click button again to rebuild request. (Debug: {raw_output[:100]})")
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

