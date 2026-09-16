import sqlite3

class UnsafeQueryError(Exception):
    pass

def execute_sql(db_path: str, sql: str):
    """
    Executes SQL against the database — but only if it's a SELECT statement.
    This is a code-level guardrail, independent of what we told the LLM to do.
    Never rely on the prompt alone for safety.
    """
    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        raise UnsafeQueryError(
            f"Refusing to execute non-SELECT statement: {sql[:50]}..."
        )

    forbidden = ["drop", "delete", "update", "insert", "alter", "attach", ";--"]
    if any(word in normalized for word in forbidden):
        raise UnsafeQueryError(f"Query contains forbidden keyword: {sql}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        return columns, rows
    finally:
        conn.close()