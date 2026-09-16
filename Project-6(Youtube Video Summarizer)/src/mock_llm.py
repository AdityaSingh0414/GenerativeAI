import os
import logging
from typing import List, Any
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

# Global flag to track if we should fall back to mock mode
_MOCK_ACTIVE = os.getenv("MOCK_LLM", "").lower() in ("true", "1", "yes")

def is_mock_active() -> bool:
    global _MOCK_ACTIVE
    return _MOCK_ACTIVE

def set_mock_active(active: bool):
    global _MOCK_ACTIVE
    _MOCK_ACTIVE = active

class MockMessage:
    def __init__(self, content: str):
        self.content = content
        self.usage_metadata = {
            "input_tokens": 120,
            "output_tokens": 80,
            "total_tokens": 200
        }

class MockEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.1] * 1536

def generate_mock_summary(chunk_text: str) -> str:
    cleaned = " ".join(chunk_text.split()[:30])
    return f"This segment covers key themes in the video transcript, specifically discussing: '{cleaned}...'. It highlights the core ideas and progresses the main narrative."

def generate_mock_final_summary(joined_summaries: str) -> str:
    bullets = []
    lines = joined_summaries.split("\n\n")
    for idx, line in enumerate(lines[:8]):
        cleaned_line = line.strip()
        if cleaned_line:
            # strip timestamp prefix like [01:05]
            if cleaned_line.startswith("[") and "]" in cleaned_line:
                cleaned_line = cleaned_line.split("]", 1)[1].strip()
            bullets.append(f"- Key point {idx + 1}: {cleaned_line[:80]}...")
    
    bullet_text = "\n".join(bullets)
    return f"""This is a cohesive summary of the YouTube video. The video provides an in-depth walkthrough of the main concepts, detailing practical steps, setups, and core theories behind the topic.

### Key Points
{bullet_text}"""

def generate_mock_title(summary_text: str) -> str:
    # Just take the first few words and format beautifully
    words = [w for w in summary_text.replace("'", "").replace('"', '').split() if len(w) > 3]
    title_words = words[:4] if words else ["Section", "Discussion"]
    return " ".join(title_words).title()

def generate_mock_answer(context: str, question: str) -> str:
    return f"This is a simulated answer because OpenAI API Key is unavailable or has exceeded its quota.\n\nContext match found in the transcript:\n{context[:300]}...\n\nYour Question was: '{question}'"
