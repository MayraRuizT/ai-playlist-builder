# 🎵 AI YouTube Playlist Builder

An AI-powered web app built with Python and Streamlit that curates custom music playlists and builds them directly inside your personal YouTube library using Groq AI (Llama 3.1) and the YouTube Data API v3.

## 🚀 How to Run This App Locally

### 1. Clone the repository
```bash
git clone https://github.com
cd YOUR_REPO_NAME
```

### 2. Set Up Your Environment & Dependencies
```bash
conda create -n music_app python=3.11 -y
conda activate music_app
pip install -r requirements.txt
```

### 3. Add Your Secrets
1. Save your Groq API Key as an environment variable: `export GROQ_API_KEY="your_key"`
2. Download your OAuth Desktop credential file from Google Cloud Console, rename it to `client_secret.json`, and place it in this root folder.

### 4. Authenticate & Launch
First, authorize your YouTube account using the console link utility:
```bash
python auth_maker.py
```
Once your secure token is generated, fire up your browser application dashboard interface:
```bash
streamlit run web_app.py
```
