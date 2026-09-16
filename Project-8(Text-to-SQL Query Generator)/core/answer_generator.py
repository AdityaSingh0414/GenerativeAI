from core.llm_client import call_llm

ANSWER_SYSTEM_PROMPT = """You are a helpful data analyst.
You will be given a user's question, the SQL query that was run, and the raw results.
Explain the answer in plain, concise English. Do not mention SQL or databases explicitly
unless the user asked a technical question."""

def generate_answer(question: str, sql: str, columns: list, rows: list) -> str:
    result_text = f"Columns: {columns}\nRows: {rows}"
    user_prompt = f"""Question: {question}
SQL used: {sql}
Results: {result_text}

Answer:"""
    return call_llm(ANSWER_SYSTEM_PROMPT, user_prompt, temperature=0.3)