import pytest

from transcript_fetcher import extract_video_id, format_timestamp, TranscriptError


@pytest.mark.parametrize(
    "url,expected_id",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ],
)
def test_extract_video_id_valid(url, expected_id):
    assert extract_video_id(url) == expected_id


def test_extract_video_id_invalid_raises():
    with pytest.raises(TranscriptError):
        extract_video_id("https://example.com/not-a-youtube-link")


@pytest.mark.parametrize(
    "seconds,expected",
    [(0, "00:00"), (65, "01:05"), (3661, "01:01:01"), (59, "00:59")],
)
def test_format_timestamp(seconds, expected):
    assert format_timestamp(seconds) == expected