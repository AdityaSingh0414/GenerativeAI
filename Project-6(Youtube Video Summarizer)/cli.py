#!/usr/bin/env python3
"""
cli.py
------
Same pipeline as app.py, runnable from scripts/cron without Streamlit.

Usage:
    python cli.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output summary.md
"""

import argparse
import logging
import sys

from dotenv import load_dotenv

from config import settings
from transcript_fetcher import fetch_transcript, TranscriptError, extract_video_id
from src.chunker import chunk_transcript
from src.summarizer import summarize_video
from src.chapters import build_chapters
from src.export import to_markdown
from src.video_meta import fetch_video_title

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cli")


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Summarize a YouTube video from the command line.")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--model", default=settings.openai_model, help="OpenAI model to use")
    parser.add_argument(
        "--max-tokens-per-chunk", type=int, default=settings.max_tokens_per_chunk
    )
    parser.add_argument(
        "--max-workers", type=int, default=settings.max_concurrent_requests,
        help="Concurrent chunk-summarization requests",
    )
    parser.add_argument("--no-chapter-titles", action="store_true", help="Skip AI chapter titles")
    parser.add_argument("--output", default=None, help="Write Markdown output to this file")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except TranscriptError as e:
        logger.error(str(e))
        return 1

    video_title = fetch_video_title(video_id)
    logger.info("Fetching transcript for %s (%s)...", video_title, video_id)
    try:
        segments = fetch_transcript(args.url)
    except TranscriptError as e:
        logger.error("Transcript error: %s", e)
        return 1

    logger.info("Chunking transcript...")
    chunks = chunk_transcript(segments, max_tokens=args.max_tokens_per_chunk, model_name=args.model)
    logger.info("%d chunk(s). Summarizing (concurrent map-reduce)...", len(chunks))

    final_summary, chunk_summaries, usage = summarize_video(
        chunks, model_name=args.model, max_workers=args.max_workers
    )
    chapters, chapters_usage = build_chapters(
        chunk_summaries, model_name=args.model,
        use_llm_titles=not args.no_chapter_titles, max_workers=args.max_workers,
    )
    total_usage = usage.add(chapters_usage)

    print("\n=== SUMMARY ===\n")
    print(final_summary)
    print("\n=== CHAPTERS ===\n")
    for ch in chapters:
        print(f"[{ch.timestamp}] {ch.title}")
    print(f"\n=== USAGE === {total_usage}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(to_markdown(video_title, final_summary, chapters))
        logger.info("Wrote Markdown output to %s", args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())