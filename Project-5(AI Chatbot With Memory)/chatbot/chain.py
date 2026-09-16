import os
from  dotenv import load_dotenv
try:
    from langchain.chains import ConversationChain
except ImportError:
    from langchain_classic.chains import ConversationChain
from .prompts import CHAT_PROMPT
from .memory import get_memory

load_dotenv()

def build_chain(provider ="groq"):
    if provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
        )

    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
        )

    memory = get_memory()

    chain = ConversationChain (
        llm= llm,
        memory= memory,
        prompt= CHAT_PROMPT,
        verbose=True,  # prints the full prompt LangChain sends — great for learning
    )

    return chain 
