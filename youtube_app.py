import os
import json
from groq import Groq
from googleapiclient.discovery import build

# 1. Initialize API Clients from Environment Variables
groq_client = Groq()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

if not youtube_api_key:
    print("❌ Error: YOUTUBE_API_KEY environment variable is not set.")
    exit()

youtube_client = build("youtube", "v3", developerKey=youtube_api_key)

# 2. Get User Curation or Extraction Prompt
user_prompt = "Make a high energy songs playlist with songs from charli xcx and kim petras"
print(f"🤖 Processing playlist idea: '{user_prompt}'...")

# 3. Request Groq AI to build a structured JSON dataset
ai_response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert music curator and data extractor. "
                "If the user provides a list of songs, extract them. "
                "If the user asks for a theme, generate a list of 5-10 real, popular tracks. "
                "You must respond ONLY with a valid JSON array of objects. "
                "Each object must have 'artist' and 'track' keys. "
                "Do not include intro text, explanations, or markdown code blocks like ```json."
            )
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

raw_output = ai_response.choices[0].message.content.strip()

try:
    songs_to_find = json.loads(raw_output)
except json.JSONDecodeError:
    print("❌ Failed to parse AI JSON dataset. Raw output:")
    print(raw_output)
    exit()

# 4. Search YouTube for Music Video IDs
print("\n🔍 Fetching matches from YouTube Music catalogs...")
playlist_tracks = []

for song in songs_to_find:
    # Adding "topic" forces YouTube search engine to look for standard album audio art files
    search_query = f"{song['artist']} - {song['track']} topic"
    
    request = youtube_client.search().list(
        q=search_query,
        part="id,snippet",
        maxResults=1,
        type="video",
        videoCategoryId="10"  # Category 10 strictly isolates searches to standard Music uploads
    )
    
    response = request.execute()
    items = response.get("items", [])
    
    if items:
        video_id = items[0]["id"]["videoId"]
        clean_title = items[0]["snippet"]["title"]
        print(f" ✅ Found: {clean_title}")
        playlist_tracks.append({"title": clean_title, "id": video_id})
    else:
        print(f" ❌ No match found for: {song['artist']} - {song['track']}")

# 5. Output Ready-to-Use Playlist Tracks
if playlist_tracks:
    print(f"\n🎉 Success! Your high energy tracks are ready to open:")
    for index, track in enumerate(playlist_tracks, start=1):
        print(f"{index}. {track['title']} -> https://youtube.com{track['id']}")
else:
    print("\n😕 No tracks were found inside the YouTube database matching your request.")

