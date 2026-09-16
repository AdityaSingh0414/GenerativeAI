"""
qa_engine.py
------------
RAG so the user can ask follow-up questions about the video.
"""

import os
from typing import List, Tuple

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from src.chunker import TranscriptChunk
from transcript_fetcher import format_timestamp
from src.cost_tracker import UsageReport, usage_from_message

ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """Answer the question using ONLY the transcript excerpts below. Each
excerpt is labeled with its timestamp. If the excerpts don't contain the
answer, say so plainly instead of guessing.

TRANSCRIPT EXCERPTS:
{context}

QUESTION: {question}

ANSWER (mention relevant timestamps like [MM:SS] where useful):"""
)


def build_qa_index(chunks: List[TranscriptChunk]) -> FAISS:
    docs = [
        Document(
            page_content=chunk.text,
            metadata={"start_time": chunk.start_time, "end_time": chunk.end_time},
        )
        for chunk in chunks
    ]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.from_documents(docs, embeddings)


def answer_question(
    vectorstore: FAISS,
    question: str,
    model_name: str = None,
    top_k: int = 4,
) -> Tuple[str, UsageReport]:
    model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    relevant_docs = vectorstore.similarity_search(question, k=top_k)
    context = "\n\n".join(
        f"[{format_timestamp(doc.metadata['start_time'])}] {doc.page_content}"
        for doc in relevant_docs
    )

    llm = ChatOpenAI(model=model_name, temperature=0.1)
    chain = ANSWER_PROMPT | llm
    message = chain.invoke({"context": context, "question": question})

    usage = usage_from_message(message, model_name)
    return message.content.strip(), usage