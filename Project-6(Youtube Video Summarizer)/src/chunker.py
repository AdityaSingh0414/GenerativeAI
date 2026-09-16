"""
chunker.py
----------
Step 2: Split transcript into manageable, token-aware chunks.
"""

from dataclasses import dataclass
from typing import List

import tiktoken

from transcript_fetcher import TranscriptSegment


@dataclass
class TranscriptChunk:
    text: str
    start_time: float
    end_time: float


def _get_encoder(model_name: str = "gpt-4o-mini"):
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def chunk_transcript(
    segments: List[TranscriptSegment],
    max_tokens: int = 1800,
    model_name: str = "gpt-4o-mini",
) -> List[TranscriptChunk]:
    if not segments:
        return []

    encoder = _get_encoder(model_name)

    chunks: List[TranscriptChunk] = []
    current_texts: List[str] = []
    current_tokens = 0
    chunk_start = segments[0].start
    chunk_end = segments[0].start

    for seg in segments:
        seg_text = seg.text.strip()
        if not seg_text:
            continue

        seg_tokens = len(encoder.encode(seg_text))

        if current_tokens + seg_tokens > max_tokens and current_texts:
            chunks.append(
                TranscriptChunk(
                    text=" ".join(current_texts),
                    start_time=chunk_start,
                    end_time=chunk_end,
                )
            )
            current_texts = []
            current_tokens = 0
            chunk_start = seg.start

        current_texts.append(seg_text)
        current_tokens += seg_tokens
        chunk_end = seg.start + seg.duration

    if current_texts:
        chunks.append(
            TranscriptChunk(
                text=" ".join(current_texts),
                start_time=chunk_start,
                end_time=chunk_end,
            )
        )

    return chunks