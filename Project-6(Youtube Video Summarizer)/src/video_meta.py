"""
video_meta.py
-------------
Fetch a human-readable video title via YouTube's public oEmbed
endpoint (no API key needed).
"""

import json
import urllib.request
import urllib.error


def fetch_video_title(video_id: str, timeout: float = 5.0) -> str:
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title", video_id)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return video_id