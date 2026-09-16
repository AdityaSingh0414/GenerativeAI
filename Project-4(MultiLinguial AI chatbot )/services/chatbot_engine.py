from dotenv import load_dotenv
import os
from openai import OpenAI

from services.language_detector import detect_language
from services.translator import translate_text

# Load environment variables
load_dotenv()

# Read API Key
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key exists
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Please check your .env file."
    )

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Default language
PIVOT_LANG = os.getenv("DEFAULT_PIVOT_LANGUAGE", "en")


def get_response(history: list, user_message: str, output_lang_code: str) -> dict:
    """
    history: list of {"role": "user"/"assistant", "content": str}
    user_message: raw message typed by user
    output_lang_code: ISO language code for output
    """

    # Detect input language
    input_lang = detect_language(user_message)

    # Translate to pivot language
    translated_input = translate_text(
        user_message,
        source=input_lang,
        target=PIVOT_LANG
    )

    history.append(
        {
            "role": "user",
            "content": translated_input
        }
    )

    # Generate response
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful, friendly multilingual assistant."
            },
            *history
        ]
    )

    reply_en = completion.choices[0].message.content

    history.append(
        {
            "role": "assistant",
            "content": reply_en
        }
    )

    # Translate response back to user's selected language
    reply_final = translate_text(
        reply_en,
        source=PIVOT_LANG,
        target=output_lang_code
    )

    return {
        "input_detected_language": input_lang,
        "reply": reply_final,
        "history": history[-10:]   # Keep last 10 messages
    }