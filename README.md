# YoutubePlaylistAddition

A small Python script that creates a YouTube playlist and adds multiple videos to it in one go using the YouTube Data API (OAuth).

## What it does
- Authenticates you via Google OAuth (first run opens a browser)
- Creates a new playlist (default: private)
- Extracts video IDs from multiple YouTube URL formats
- Adds each video to the playlist
- Skips invalid / deleted videos and prints a summary

## Requirements
- Python 3.10+ recommended
- A Google Cloud project with **YouTube Data API v3** enabled
- OAuth **Desktop app** credentials JSON

## Setup

### 1) Clone and install dependencies
git clone https://github.com/NiveditaAryaK/YoutubePlaylistAddition.git
cd YoutubePlaylistAddition
python -m venv env
source env/bin/activate
pip install -r requirements.txt

### 2) Create OAuth credentials
In Google Cloud Console:
Enable YouTube Data API v3
Create OAuth client ID → Application type: Desktop app
Download the credentials JSON and place it in the project root as:
client_secret.json

### 3) Add your links
Edit main.py and update the links = [...] list (or modify to read from a text file).

### 4) Run python main.py
On first run, it opens a browser for consent. After that it stores a token locally so you don’t have to log in every time.

## #Output
Prints each added video
Skips invalid / unavailable links
Prints a final summary of skipped links

### Notes / Safety
These files should NOT be committed:
client_secret.json (OAuth secret)
token_youtube.pkl (access/refresh token cache)
env/ (virtual environment)
Make sure your .gitignore includes them.

### Customization
Playlist privacy is set in create_playlist():
"private" (default)
"unlisted"
"public"
Playlist title/description:
playlist_title
playlist_description
