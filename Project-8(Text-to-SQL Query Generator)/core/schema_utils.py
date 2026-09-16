import sqlite3

def get_schema_text(db_path: str) -> str:
    """
    Reads the SQLite schema and formats it as plain text
    that we can safely inject into an LLM prompt.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    schema_lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
        col_desc = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        schema_lines.append(f"Table: {table}\nColumns: {col_desc}")

    conn.close()
    return "\n\n".join(schema_lines)


if __name__ == "__main__":
    print(get_schema_text("db/sample.db"))