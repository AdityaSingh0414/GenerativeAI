"""
transcript_fetcher.py
----------------------
Step 1: Fetch transcript via youtube-transcript-api.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float


class TranscriptError(Exception):
    pass


_YOUTUBE_ID_PATTERNS = [
    r"(?:youtube\.com\/watch\?v=)([\w-]{11})",
    r"(?:youtu\.be\/)([\w-]{11})",
    r"(?:youtube\.com\/embed\/)([\w-]{11})",
    r"(?:youtube\.com\/shorts\/)([\w-]{11})",
]


def extract_video_id(url_or_id: str) -> str:
    url_or_id = url_or_id.strip()

    if re.fullmatch(r"[\w-]{11}", url_or_id):
        return url_or_id

    for pattern in _YOUTUBE_ID_PATTERNS:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise TranscriptError(
        f"Could not extract a video ID from: {url_or_id!r}. "
        "Paste a full YouTube URL (watch, youtu.be, embed, or shorts link)."
    )


def fetch_transcript(
    url_or_id: str,
    languages: Optional[List[str]] = None,
) -> List[TranscriptSegment]:
    video_id = extract_video_id(url_or_id)
    languages = languages or ["en", "en-US", "en-GB"]

    try:
        raw = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    except TranscriptsDisabled:
        raise TranscriptError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        try:
            transcript_list = YouTubeTranscriptApi().list(video_id)
            first_available = next(iter(transcript_list))
            raw = first_available.fetch()
        except Exception as exc:
            raise TranscriptError(
                f"No transcript found in {languages} or any fallback language."
            ) from exc
    except VideoUnavailable:
        raise TranscriptError("This video is unavailable or private.")
    except Exception as exc:
        raise TranscriptError(f"Unexpected error fetching transcript: {exc}") from exc

    return [
        TranscriptSegment(text=seg.text, start=seg.start, duration=seg.duration)
        for seg in raw
    ]


def segments_to_text(segments: List[TranscriptSegment]) -> str:
    return " ".join(s.text.replace("\n", " ").strip() for s in segments)


def format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
