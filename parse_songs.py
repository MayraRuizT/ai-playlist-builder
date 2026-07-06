import os
import json
from groq import Groq

client = Groq()

# Changing the input from messy text to a generation prompt!
user_request = "Make a high energy songs playlist with songs from charli xcx and kim petras"

response = client.chat.completions.create(
    model="llama-3.1-8b-instant", 
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert music curator and data extractor. "
                "If the user provides a list of songs, extract them. "
                "If the user asks you to create, recommend, or generate a playlist based on a theme, mood, or specific artists, brainstorm a list of 5-10 real, popular tracks that perfectly fit that request. "
                "You must respond ONLY with a valid JSON array of objects. "
                "Each object must have 'artist' and 'track' keys. "
                "Do not include introductory text, explanations, or markdown syntax like ```json."
            )
        },
        {
            "role": "user",
            "content": user_request
        }
    ]
)

raw_output = response.choices[0].message.content.strip()

try:
    songs_list = json.loads(raw_output)
    print(f"--- Generated Playlist for: '{user_request}' ---")
    for song in songs_list:
        print(f"Artist: {song['artist']} | Track: {song['track']}")
        
except json.JSONDecodeError:
    print("Error parsing JSON. Raw AI Output was:")
    print(raw_output)

