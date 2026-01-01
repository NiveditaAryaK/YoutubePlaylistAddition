from __future__ import print_function

import os
import re
import pickle
from urllib.parse import urlparse, parse_qs

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

# ---- CONFIG ----
# Scope needed to manage YouTube account
SCOPES = ["https://www.googleapis.com/auth/youtube"]

CREDENTIALS_FILE = "client_secret.json"  # OAuth client file from Google Cloud
TOKEN_FILE = "token_youtube.pkl"         # Where we'll cache your access token
LINKS_FILE = "links.txt"                 # One YouTube URL per line


def get_authenticated_service():
    """
    Authenticate the user and return a YouTube API service object.
    Uses OAuth and stores a token so you don't need to log in every time.
    """
    creds = None

    # Load saved creds if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no creds or expired, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def load_links_from_file(file_path: str) -> list[str]:
    """
    Load YouTube links from a text file.

    Supports:
    - blank lines
    - full-line comments starting with '#'
    - inline comments after '#'
    - optional quotes and trailing commas (e.g. "https://..." ,  # note)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Links file not found: {file_path}\n"
            f"Create '{file_path}' in the project root and add one YouTube URL per line."
        )

    links: list[str] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # skip empty lines and full-line comments
            if not line or line.startswith("#"):
                continue

            # remove inline comments
            if "#" in line:
                line = line.split("#", 1)[0].strip()

            # remove trailing comma (common in python lists)
            if line.endswith(","):
                line = line[:-1].strip()

            # strip surrounding quotes
            if (line.startswith('"') and line.endswith('"')) or (line.startswith("'") and line.endswith("'")):
                line = line[1:-1].strip()

            if line:
                links.append(line)

    return links


def extract_video_id(url: str) -> str | None:
    """
    Extracts video ID from various YouTube URL formats.
    Returns None if no ID is found.
    """
    # Examples:
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    # https://youtu.be/dQw4w9WgXcQ
    # https://www.youtube.com/shorts/dQw4w9WgXcQ
    parsed = urlparse(url)

    # Standard watch URLs
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            return query.get("v", [None])[0]
        # Shorts or other forms like /shorts/<id> or /embed/<id>
        match = re.match(r"^/(shorts|embed)/([^/?]+)", parsed.path)
        if match:
            return match.group(2)

    # youtu.be/<id>
    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    return None


def create_playlist(youtube, title: str, description: str = "") -> str:
    """
    Create a playlist and return its playlist ID.
    """
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": "private"  # change to "public" or "unlisted" if you want
            },
        },
    )
    response = request.execute()
    playlist_id = response["id"]
    print(f"Created playlist: {title} (ID: {playlist_id})")
    return playlist_id


def add_video_to_playlist(
    youtube,
    playlist_id: str,
    video_id: str,
    original_url: str,
    failed_links: list,
):
    """
    Add a single video to a playlist.
    On failure (e.g. 404 video not found), it records the URL in failed_links and continues.
    """
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            }
        },
    )

    try:
        response = request.execute()
        print(f"  Added video: https://youtu.be/{video_id}")
        return response
    except HttpError as e:
        status = getattr(e.resp, "status", None)
        if status == 404:
            print(f"  [SKIP] Video not found (404): {original_url}")
        else:
            print(f"  [SKIP] Error adding {original_url}: {e}")
        failed_links.append(original_url)
        return None


def create_playlist_from_links(
    links: list[str],
    playlist_title: str,
    playlist_description: str = "",
):
    youtube = get_authenticated_service()

    # 1. Create the playlist
    playlist_id = create_playlist(youtube, playlist_title, playlist_description)

    failed_links: list[str] = []  # track all skipped links

    # 2. Extract video IDs and add them
    for url in links:
        video_id = extract_video_id(url)
        if not video_id:
            print(f"[SKIP] Invalid YouTube URL (no video ID): {url}")
            failed_links.append(url)
            continue

        add_video_to_playlist(
            youtube=youtube,
            playlist_id=playlist_id,
            video_id=video_id,
            original_url=url,
            failed_links=failed_links,
        )

    print("\n========== SUMMARY ==========")
    if failed_links:
        print("These links were skipped (invalid or not found):")
        for u in failed_links:
            print(" -", u)
    else:
        print("All links added successfully!")
    print("Done!")


if __name__ == "__main__":
    # Load links dynamically from LINKS_FILE (one URL per line)
    links = load_links_from_file(LINKS_FILE)

    playlist_title = "Neetcode 150 Pattern Recognition Edition"
    playlist_description = "Playlist created via Python + YouTube Data API"

    create_playlist_from_links(links, playlist_title, playlist_description)
