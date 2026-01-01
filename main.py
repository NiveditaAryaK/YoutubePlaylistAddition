from __future__ import print_function

import os
import re
from urllib.parse import urlparse, parse_qs

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError   # <<< added
import pickle

# ---- CONFIG ----
# Scope needed to manage YouTube account
SCOPES = ["https://www.googleapis.com/auth/youtube"]

CREDENTIALS_FILE = "client_secret.json"  # OAuth client file from Google Cloud
TOKEN_FILE = "token_youtube.pkl"         # Where we'll cache your access token


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

    try:  # <<< added error handling
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

    failed_links: list[str] = []   # <<< track all skipped links

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
    # Example: replace with your own list of links
    links = [

# =========================
# 🔥 VERY HIGH PROBABILITY (Amazon Core)
# Arrays + HashMap
# =========================
"https://www.youtube.com/watch?v=3OamzN90kPg",  # Contains Duplicate
"https://www.youtube.com/watch?v=KLlXCFG5TnA",  # Two Sum
"https://www.youtube.com/watch?v=9UtInBqnCgA",  # Valid Anagram
"https://www.youtube.com/watch?v=vzdNOK2oB2E",  # Group Anagrams
"https://www.youtube.com/watch?v=YPTqKIgVk-k",  # Top K Frequent Elements
"https://www.youtube.com/watch?v=bNvIQI2wAjk",  # Product of Array Except Self
"https://www.youtube.com/watch?v=TjFXEUCMqI8",  # Valid Sudoku
"https://www.youtube.com/watch?v=P6RZZMu_maU",  # Longest Consecutive Sequence

# =========================
# 🔥 VERY HIGH PROBABILITY
# Sliding Window
# =========================
"https://www.youtube.com/watch?v=1pkOgXD63yU",  # Best Time to Buy and Sell Stock
"https://www.youtube.com/watch?v=wiGpQwVHdE0",  # Longest Substring Without Repeating Characters
"https://www.youtube.com/watch?v=gqXU1UyA8pk",  # Longest Repeating Character Replacement
"https://www.youtube.com/watch?v=UbyhOgBN834",  # Permutation in String
"https://www.youtube.com/watch?v=jSto0O4AJbM",  # Minimum Window Substring
"https://www.youtube.com/watch?v=DfljaUwZsOk",  # Sliding Window Maximum

# =========================
# 🔥 VERY HIGH PROBABILITY
# Two Pointers
# =========================
"https://www.youtube.com/watch?v=jJXJ16kPFWg",  # Valid Palindrome
"https://www.youtube.com/watch?v=cQ1Oz4ckceM",  # Two Sum II
"https://www.youtube.com/watch?v=jzZsG8n2R9A",  # 3Sum
"https://www.youtube.com/watch?v=UuiTKBwPgAo",  # Container With Most Water
"https://www.youtube.com/watch?v=ZI2z5pq0TqA",  # Trapping Rain Water

# =========================
# 🔥 HIGH PROBABILITY
# Stack
# =========================
"https://www.youtube.com/watch?v=WTzjTskDFMg",  # Valid Parentheses
"https://www.youtube.com/watch?v=qkLl7nAwDPo",  # Min Stack
"https://www.youtube.com/watch?v=cTBiBSnjO3c",  # Daily Temperatures
"https://www.youtube.com/watch?v=Pr6T-3yB9RM",  # Car Fleet
"https://www.youtube.com/watch?v=zx5Sw9130L0",  # Largest Rectangle in Histogram

# =========================
# 🔥 HIGH PROBABILITY
# Binary Search
# =========================
"https://www.youtube.com/watch?v=s4DPM8ct1pI",  # Binary Search
"https://www.youtube.com/watch?v=Ber2pi2C0j0",  # Search a 2D Matrix
"https://www.youtube.com/watch?v=U2SozAs9RzA",  # Koko Eating Bananas
"https://www.youtube.com/watch?v=nIVW4P8b1VA",  # Find Min in Rotated Sorted Array
"https://www.youtube.com/watch?v=U8XENwh8Oy8",  # Search in Rotated Sorted Array

# =========================
# 🔥 HIGH PROBABILITY
# Linked List
# =========================
"https://www.youtube.com/watch?v=G0_I-ZF0S38",  # Reverse Linked List
"https://www.youtube.com/watch?v=XIdigk956u0",  # Merge Two Sorted Lists
"https://www.youtube.com/watch?v=XVuQxVej6y8",  # Remove Nth Node From End
"https://www.youtube.com/watch?v=gBTe7lFR3vc",  # Linked List Cycle
"https://www.youtube.com/watch?v=7ABFKPK2hD4",  # LRU Cache

# =========================
# 🔥 MEDIUM–HIGH PROBABILITY
# Trees (DFS/BFS)
# =========================
"https://www.youtube.com/watch?v=OnSn2XEQ4MY",  # Invert Binary Tree
"https://www.youtube.com/watch?v=hTM3phVI6YQ",  # Max Depth
"https://www.youtube.com/watch?v=bkxqA8Rfv04",  # Diameter
"https://www.youtube.com/watch?v=QfJsau0ItOY",  # Balanced Binary Tree
"https://www.youtube.com/watch?v=6ZnyEApgFYg",  # Level Order Traversal
"https://www.youtube.com/watch?v=gs2LMfuOR9k",  # LCA
"https://www.youtube.com/watch?v=s6ATEkipzow",  # Validate BST
"https://www.youtube.com/watch?v=5LUXSvjmGCw",  # Kth Smallest in BST

# =========================
# 🔥 MEDIUM PROBABILITY
# Heap / Priority Queue
# =========================
"https://www.youtube.com/watch?v=XEmy13g1Qxc",  # Kth Largest Element
"https://www.youtube.com/watch?v=rI2EBUEMfTk",  # K Closest Points
"https://www.youtube.com/watch?v=itmhHWaHupI",  # Median from Data Stream
"https://www.youtube.com/watch?v=s8p8ukTyA2I",  # Task Scheduler

# =========================
# 🔥 MEDIUM PROBABILITY
# Graphs
# =========================
"https://www.youtube.com/watch?v=pV2kpPD66nE",  # Number of Islands
"https://www.youtube.com/watch?v=mQeF6bN8hMk",  # Clone Graph
"https://www.youtube.com/watch?v=EgI5nU9etnU",  # Course Schedule
"https://www.youtube.com/watch?v=h9iTnkgv05E",  # Word Ladder
"https://www.youtube.com/watch?v=8f1XPm4WOUc",  # Pacific Atlantic Water Flow

# =========================
# 🔥 MEDIUM–LOW PROBABILITY
# Backtracking
# =========================
"https://www.youtube.com/watch?v=REOH22Xwdkk",  # Subsets
"https://www.youtube.com/watch?v=s7AvT7cGdSo",  # Permutations
"https://www.youtube.com/watch?v=GBKI9VSKdGg",  # Combination Sum
"https://www.youtube.com/watch?v=pfiQ_PS1g8E",  # Word Search
"https://www.youtube.com/watch?v=Ph95IHmRp5M",  # N-Queens

# =========================
# 🔥 EXPECTED BUT LATE-STAGE
# Dynamic Programming (Amazon asks basics)
# =========================
"https://www.youtube.com/watch?v=Y0lT9Fck7qI",  # Climbing Stairs
"https://www.youtube.com/watch?v=ktmzAZWkEZ0",  # Min Cost Climbing Stairs
"https://www.youtube.com/watch?v=73r3KWiEvyk",  # House Robber
"https://www.youtube.com/watch?v=Hw6Ygp3JBYw",  # House Robber II
"https://www.youtube.com/watch?v=U8XENwh8Oy8",  # Coin Change
"https://www.youtube.com/watch?v=XYQecbcd6_c",  # Longest Palindromic Substring
"https://www.youtube.com/watch?v=YcJTyrG3bZs",  # Decode Ways
"https://www.youtube.com/watch?v=Sx9NNgInc3A",  # Word Break
]



    playlist_title = "Neetcode 150 Pattern RecognitionEdition"
    playlist_description = "Playlist created via Python + YouTube Data API"

    create_playlist_from_links(links, playlist_title, playlist_description)
