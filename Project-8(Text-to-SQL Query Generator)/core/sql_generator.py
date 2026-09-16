from core.llm_client import call_llm

SQL_SYSTEM_PROMPT = """You are an expert SQL generator.
You will be given a database schema and a natural language question.

RULES (follow strictly):
1. Output ONLY a single valid SQLite SQL query.
2. Do NOT include explanations, markdown fences, or the word "sql".
3. Do NOT invent tables or columns that are not in the schema.
4. If the question cannot be answered with the given schema, output exactly: NO_QUERY
5. Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, or DROP.
"""

def generate_sql(schema_text: str, question: str) -> str:
    user_prompt = f"""Database schema:
{schema_text}

Question: {question}

SQL query:"""

    raw_output = call_llm(SQL_SYSTEM_PROMPT, user_prompt)

    # Defensive cleanup: LLMs sometimes wrap output in ```sql ... ``` anyway.
    cleaned = raw_output.replace("```sql", "").replace("```", "").strip()
    return cleaned