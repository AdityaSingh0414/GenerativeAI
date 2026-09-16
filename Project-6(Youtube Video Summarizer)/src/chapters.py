"""
chapters.py
-----------
Builds a chapter list (timestamp + short title) from chunk summaries.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.summarizer import ChunkSummary, _invoke_with_retry
from transcript_fetcher import format_timestamp
from src.cost_tracker import UsageReport, usage_from_message, combine


@dataclass
class Chapter:
    timestamp: str
    start_seconds: float
    title: str
    summary: str


TITLE_PROMPT = ChatPromptTemplate.from_template(
    """Give a short chapter title (max 6 words, title case, no punctuation
at the end) for this part of a video, based on its summary:

{summary}

CHAPTER TITLE:"""
)


def _title_for_chunk(summary_text: str, model_name: str) -> Tuple[str, UsageReport]:
    model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name, temperature=0.3)
    chain = TITLE_PROMPT | llm
    message = _invoke_with_retry(chain, {"summary": summary_text})
    title = message.content.strip().strip('"')
    usage = usage_from_message(message, model_name)
    return title, usage


def build_chapters(
    chunk_summaries: List[ChunkSummary],
    model_name: str = None,
    use_llm_titles: bool = True,
    max_workers: int = 4,
) -> Tuple[List[Chapter], UsageReport]:
    if not use_llm_titles:
        chapters = [
            Chapter(
                timestamp=format_timestamp(cs.start_time),
                start_seconds=cs.start_time,
                title=" ".join(cs.summary.split()[:6]) + ("..." if len(cs.summary.split()) > 6 else ""),
                summary=cs.summary,
            )
            for cs in chunk_summaries
        ]
        return chapters, UsageReport()

    results: List[Tuple[int, str]] = []
    usages: List[UsageReport] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_index = {
            pool.submit(_title_for_chunk, cs.summary, model_name): i
            for i, cs in enumerate(chunk_summaries)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            title, usage = future.result()
            results.append((index, title))
            usages.append(usage)

    results.sort(key=lambda pair: pair[0])
    titles = [title for _, title in results]

    chapters = [
        Chapter(
            timestamp=format_timestamp(cs.start_time),
            start_seconds=cs.start_time,
            title=title,
            summary=cs.summary,
        )
        for cs, title in zip(chunk_summaries, titles)
    ]
    return chapters, combine(usages)