import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Groq's API is OpenAI-compatible — same SDK, different base_url.
# This is a useful pattern to recognize: many providers copy OpenAI's interface.
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"  # fast + free tier friendly

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    """
    temperature=0.0 because for SQL generation we want deterministic,
    literal output — not creative writing.
    """
    response = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()