import src.chunker as chunker_module
from src.chunker import chunk_transcript
from transcript_fetcher import TranscriptSegment


class _FakeEncoder:
    def encode(self, text: str):
        return text.split()


def test_chunk_transcript_respects_token_budget(monkeypatch):
    monkeypatch.setattr(chunker_module, "_get_encoder", lambda model_name=None: _FakeEncoder())

    segments = [
        TranscriptSegment(text="one two three", start=0.0, duration=2.0),
        TranscriptSegment(text="four five six", start=2.0, duration=2.0),
        TranscriptSegment(text="seven eight nine", start=4.0, duration=2.0),
    ]
    chunks = chunk_transcript(segments, max_tokens=5)

    assert len(chunks) == 2
    assert chunks[0].text == "one two three"
    assert chunks[1].text == "four five six seven eight nine"


def test_chunk_transcript_empty_input(monkeypatch):
    monkeypatch.setattr(chunker_module, "_get_encoder", lambda model_name=None: _FakeEncoder())
    assert chunk_transcript([], max_tokens=100) == []


def test_chunk_transcript_single_large_segment_still_returned(monkeypatch):
    monkeypatch.setattr(chunker_module, "_get_encoder", lambda model_name=None: _FakeEncoder())
    segments = [TranscriptSegment(text="a " * 50, start=0.0, duration=10.0)]
    chunks = chunk_transcript(segments, max_tokens=5)
    assert len(chunks) == 1