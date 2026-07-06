import os
import json
import streamlit as st
import pickle
from groq import Groq
from googleapiclient.discovery import build

st.set_page_config(page_title="AI YouTube Playlist Builder", page_icon="🎵")
st.title("🎵 AI YouTube Playlist Builder")

# Verify token.pickle exists before building interface frames
if not os.path.exists('token.pickle'):
    st.error("❌ App Not Authenticated! Please run 'python auth_maker.py' in your terminal session console first to register.")
    st.stop()

# Initialize clients seamlessly behind the scenes
groq_client = Groq()

with open('token.pickle', 'rb') as token:
    creds = pickle.load(token)
youtube_client = build('youtube', 'v3', credentials=creds)

st.success("🔒 Secured Google/YouTube Engine Connected Successfully!")

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

