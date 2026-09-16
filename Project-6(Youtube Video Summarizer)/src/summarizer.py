"""
summarizer.py
-------------
Steps 3 & 4: MAP (concurrent, retried, cost-tracked) then REDUCE.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from openai import APIError, APITimeoutError, RateLimitError

from src.chunker import TranscriptChunk
from transcript_fetcher import format_timestamp
from src.cost_tracker import UsageReport, usage_from_message, combine

logger = logging.getLogger(__name__)


@dataclass
class ChunkSummary:
    summary: str
    start_time: float
    end_time: float


MAP_PROMPT = ChatPromptTemplate.from_template(
    """You are summarizing one segment of a longer YouTube video transcript.

Write a concise summary (3-5 sentences) of ONLY the content below.
Focus on the key points, claims, or events described. Do not add
information that isn't in the text. Do not say "this segment discusses";
just state the content directly.

TRANSCRIPT SEGMENT:
{chunk_text}

CONCISE SUMMARY:"""
)

REDUCE_PROMPT = ChatPromptTemplate.from_template(
    """You are combining several partial summaries of consecutive segments
of a single YouTube video into one cohesive final summary.

Write a well-structured summary of the whole video with:
- A 2-3 sentence overview at the top
- A "Key Points" section with 5-10 bullet points covering the most
  important ideas across the whole video, in the order they occur

Do not mention "segments," "chunks," or "parts" — write as if you
watched the whole video straight through.

PARTIAL SUMMARIES (in chronological order):
{joined_summaries}

FINAL SUMMARY:"""
)


def _get_llm(model_name: str = None, temperature: float = 0.2) -> ChatOpenAI:
    model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model_name, temperature=temperature)


_RETRYABLE = retry_if_exception_type((RateLimitError, APIError, APITimeoutError))


@retry(
    retry=_RETRYABLE,
    wait=wait_random_exponential(min=1, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _invoke_with_retry(chain, variables: dict):
    return chain.invoke(variables)


def _summarize_one_chunk(
    chunk: TranscriptChunk, model_name: str
) -> Tuple[ChunkSummary, UsageReport]:
    llm = _get_llm(model_name)
    chain = MAP_PROMPT | llm
    message = _invoke_with_retry(chain, {"chunk_text": chunk.text})

    summary = ChunkSummary(
        summary=message.content.strip(),
        start_time=chunk.start_time,
        end_time=chunk.end_time,
    )
    usage = usage_from_message(message, model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return summary, usage


def map_summarize_chunks(
    chunks: List[TranscriptChunk],
    model_name: str = None,
    max_workers: int = 4,
) -> Tuple[List[ChunkSummary], UsageReport]:
    if not chunks:
        return [], UsageReport()

    results: List[Tuple[int, ChunkSummary]] = []
    usages: List[UsageReport] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_index = {
            pool.submit(_summarize_one_chunk, chunk, model_name): i
            for i, chunk in enumerate(chunks)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                summary, usage = future.result()
            except Exception:
                logger.exception("Chunk %d failed to summarize after retries", index)
                raise
            results.append((index, summary))
            usages.append(usage)

    results.sort(key=lambda pair: pair[0])
    ordered_summaries = [summary for _, summary in results]
    return ordered_summaries, combine(usages)


def reduce_summaries(
    chunk_summaries: List[ChunkSummary],
    model_name: str = None,
) -> Tuple[str, UsageReport]:
    llm = _get_llm(model_name)
    chain = REDUCE_PROMPT | llm

    joined = "\n\n".join(
        f"[{format_timestamp(cs.start_time)}] {cs.summary}" for cs in chunk_summaries
    )
    message = _invoke_with_retry(chain, {"joined_summaries": joined})
    usage = usage_from_message(message, model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return message.content.strip(), usage


def summarize_video(
    chunks: List[TranscriptChunk],
    model_name: str = None,
    max_workers: int = 4,
) -> Tuple[str, List[ChunkSummary], UsageReport]:
    chunk_summaries, map_usage = map_summarize_chunks(
        chunks, model_name=model_name, max_workers=max_workers
    )
    final_summary, reduce_usage = reduce_summaries(chunk_summaries, model_name=model_name)
    total_usage = map_usage.add(reduce_usage)
    return final_summary, chunk_summaries, total_usage