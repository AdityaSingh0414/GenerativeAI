"""
export.py
---------
Generate Markdown or PDF summaries in memory for st.download_button.
"""

import io
from typing import List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

from src.chapters import Chapter


def to_markdown(video_title: str, final_summary: str, chapters: List[Chapter]) -> str:
    lines = [f"# {video_title}", "", "## Summary", "", final_summary, "", "## Chapters", ""]
    for ch in chapters:
        lines.append(f"- **[{ch.timestamp}] {ch.title}** — {ch.summary}")
    return "\n".join(lines)


def to_pdf_bytes(video_title: str, final_summary: str, chapters: List[Chapter]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, title=video_title)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("Body", parent=styles["Normal"], spaceAfter=8, leading=15)

    story = [
        Paragraph(video_title, styles["Title"]),
        Spacer(1, 12),
        Paragraph("Summary", styles["Heading2"]),
        Spacer(1, 6),
    ]

    for paragraph in final_summary.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph, body_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Chapters", styles["Heading2"]))
    story.append(Spacer(1, 6))

    chapter_items = [
        ListItem(Paragraph(f"<b>[{ch.timestamp}] {ch.title}</b> — {ch.summary}", body_style))
        for ch in chapters
    ]
    story.append(ListFlowable(chapter_items, bulletType="bullet"))

    doc.build(story)
    return buffer.getvalue()