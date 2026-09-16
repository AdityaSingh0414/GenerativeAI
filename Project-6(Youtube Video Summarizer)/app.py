"""
app.py
------
Streamlit UI: fetch → chunk → concurrent map-reduce → chapters,
with caching, cost tracking, RAG Q&A, and export.

Run with: streamlit run app.py
"""

import dataclasses
import os

import streamlit as st
from dotenv import load_dotenv

from config import settings
from transcript_fetcher import (
    fetch_transcript,
    segments_to_text,
    TranscriptError,
    extract_video_id,
    TranscriptSegment,
)
from src.chunker import chunk_transcript, TranscriptChunk
from src.summarizer import summarize_video, ChunkSummary
from src.chapters import build_chapters, Chapter
from src.cache import Cache
from src.cost_tracker import UsageReport
from src.qa_engine import build_qa_index, answer_question
from src.export import to_markdown, to_pdf_bytes
from src.video_meta import fetch_video_title

load_dotenv()

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎬", layout="centered")

cache = Cache(settings.cache_db_path)

st.title("🎬 YouTube Video Summarizer")
st.caption(
    "Fetches the transcript, chunks it, summarizes concurrently (map-reduce), "
    "builds timestamped chapters, tracks token cost, caches results, and lets "
    "you ask follow-up questions about the video."
)

with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input(
        "OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password"
    )
    model_name = st.selectbox(
        "Model", options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"], index=0
    )
    max_tokens_per_chunk = st.slider(
        "Max tokens per chunk", min_value=500, max_value=4000,
        value=settings.max_tokens_per_chunk, step=100,
    )
    max_workers = st.slider(
        "Concurrent chunk requests", min_value=1, max_value=10,
        value=settings.max_concurrent_requests,
        help="How many chunks to summarize in parallel. Higher = faster, but more likely to hit rate limits.",
    )
    generate_chapter_titles = st.checkbox("Generate AI chapter titles", value=True)
    use_cache = st.checkbox(
        "Use cache (skip re-fetching/re-summarizing the same video+settings)",
        value=settings.cache_enabled,
    )

    st.divider()
    stats = cache.stats()
    st.caption(f"Cache: {stats['cached_transcripts']} transcript(s), {stats['cached_summaries']} summary set(s)")
    if st.button("Clear cache"):
        cache.clear()
        st.rerun()

if api_key_input:
    os.environ["OPENAI_API_KEY"] = api_key_input

url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
run_button = st.button("Summarize", type="primary", use_container_width=True)

if "total_usage" not in st.session_state:
    st.session_state.total_usage = UsageReport()

if run_button:
    if not url.strip():
        st.warning("Please paste a YouTube URL first.")
        st.stop()
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("Please provide an OpenAI API key in the sidebar.")
        st.stop()

    try:
        video_id = extract_video_id(url)
    except TranscriptError as e:
        st.error(str(e))
        st.stop()

    st.video(f"https://www.youtube.com/watch?v={video_id}")
    video_title = fetch_video_title(video_id)

    config_hash = Cache.make_config_hash(
        model=model_name,
        max_tokens_per_chunk=max_tokens_per_chunk,
        generate_chapter_titles=generate_chapter_titles,
    )

    cached_transcript = cache.get_transcript(video_id) if use_cache else None
    if cached_transcript:
        segments = [TranscriptSegment(**s) for s in cached_transcript]
        st.info(f"Transcript loaded from cache: {len(segments)} segments.")
    else:
        with st.spinner("Fetching transcript..."):
            try:
                segments = fetch_transcript(url)
            except TranscriptError as e:
                st.error(f"Could not fetch transcript: {e}")
                st.stop()
        if use_cache:
            cache.set_transcript(video_id, [dataclasses.asdict(s) for s in segments])
        st.info(f"Transcript fetched: {len(segments)} segments.")

    full_text = segments_to_text(segments)

    cached_result = cache.get_summary(video_id, config_hash) if use_cache else None
    if cached_result:
        final_summary = cached_result["final_summary"]
        chapters = [Chapter(**c) for c in cached_result["chapters"]]
        run_usage = UsageReport()
        st.success("Summary + chapters loaded from cache — no API calls made.")
    else:
        with st.spinner("Splitting transcript into chunks..."):
            chunks = chunk_transcript(segments, max_tokens=max_tokens_per_chunk, model_name=model_name)
        st.info(f"Split into {len(chunks)} chunk(s).")

        with st.spinner(f"Summarizing {len(chunks)} chunk(s) concurrently (map) and merging (reduce)..."):
            try:
                final_summary, chunk_summaries, summarize_usage = summarize_video(
                    chunks, model_name=model_name, max_workers=max_workers
                )
            except Exception as e:
                st.error(f"Summarization failed after retries: {e}")
                st.stop()

        with st.spinner("Building chapters..."):
            chapters, chapters_usage = build_chapters(
                chunk_summaries, model_name=model_name,
                use_llm_titles=generate_chapter_titles, max_workers=max_workers,
            )

        run_usage = summarize_usage.add(chapters_usage)

        if use_cache:
            cache.set_summary(
                video_id, config_hash,
                {
                    "final_summary": final_summary,
                    "chapters": [dataclasses.asdict(c) for c in chapters],
                },
            )

    st.session_state.total_usage = st.session_state.total_usage.add(run_usage)
    st.session_state.video_id = video_id
    st.session_state.video_title = video_title
    st.session_state.final_summary = final_summary
    st.session_state.chapters = chapters
    st.session_state.chunks_for_qa = chunk_transcript(
        segments, max_tokens=max_tokens_per_chunk, model_name=model_name
    )
    st.session_state.qa_index = None

    st.subheader("💰 Usage this run")
    if run_usage.successful_requests == 0:
        st.caption("Served entirely from cache — $0.00 spent.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Tokens used", f"{run_usage.total_tokens:,}")
        c2.metric("Est. cost", f"${run_usage.total_cost_usd:.4f}")
        c3.metric("API calls", run_usage.successful_requests)
    st.caption(f"Session total: {st.session_state.total_usage}")

    st.subheader("📋 Summary")
    st.markdown(final_summary)

    st.subheader("🕒 Chapters")
    for chapter in chapters:
        video_link = f"https://www.youtube.com/watch?v={video_id}&t={int(chapter.start_seconds)}s"
        with st.expander(f"[{chapter.timestamp}] {chapter.title}"):
            st.markdown(f"[▶ Jump to this point in the video]({video_link})")
            st.write(chapter.summary)

    with st.expander("📄 Raw transcript"):
        st.text(full_text)

    st.subheader("⬇️ Export")
    md_content = to_markdown(video_title, final_summary, chapters)
    pdf_bytes = to_pdf_bytes(video_title, final_summary, chapters)
    ecol1, ecol2 = st.columns(2)
    ecol1.download_button(
        "Download as Markdown", data=md_content,
        file_name=f"{video_id}_summary.md", mime="text/markdown", use_container_width=True,
    )
    ecol2.download_button(
        "Download as PDF", data=pdf_bytes,
        file_name=f"{video_id}_summary.pdf", mime="application/pdf", use_container_width=True,
    )

elif "final_summary" in st.session_state:
    st.info(f"Showing last result for: {st.session_state.get('video_title', '')}")
    st.markdown(st.session_state.final_summary)
else:
    st.markdown(
        "👆 Paste a YouTube link and click **Summarize** to get started. "
        "You'll need an OpenAI API key (set it in the sidebar or in a `.env` file)."
    )

if "chunks_for_qa" in st.session_state:
    st.divider()
    st.subheader("💬 Ask a question about this video")
    st.caption("Uses retrieval-augmented generation: your question is matched against the "
               "transcript, and the model answers only from the matched excerpts.")

    if st.session_state.get("qa_index") is None:
        if st.button("Enable Q&A for this video (builds a search index)"):
            with st.spinner("Embedding transcript for search..."):
                st.session_state.qa_index = build_qa_index(st.session_state.chunks_for_qa)
            st.rerun()
    else:
        question = st.text_input("Your question", key="qa_question")
        if st.button("Ask") and question.strip():
            with st.spinner("Searching transcript and answering..."):
                answer, qa_usage = answer_question(
                    st.session_state.qa_index, question,
                    model_name=model_name, top_k=settings.qa_top_k,
                )
            st.session_state.total_usage = st.session_state.total_usage.add(qa_usage)
            st.markdown(f"**Answer:** {answer}")
            st.caption(f"This question cost ${qa_usage.total_cost_usd:.4f} ({qa_usage.total_tokens} tokens)")