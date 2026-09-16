from core.schema_utils import get_schema_text
from core.sql_generator import generate_sql
from core.sql_executor import execute_sql, UnsafeQueryError
from core.answer_generator import generate_answer

DB_PATH = "db/sample.db"

def run_pipeline(question: str) -> dict:
    schema = get_schema_text(DB_PATH)
    sql = generate_sql(schema, question)

    if sql.strip().upper() == "NO_QUERY":
        return {"question": question, "sql": None, "answer": "I can't answer that with the current database."}

    try:
        columns, rows = execute_sql(DB_PATH, sql)
    except UnsafeQueryError as e:
        return {"question": question, "sql": sql, "answer": f"Blocked unsafe query: {e}"}
    except Exception as e:
        return {"question": question, "sql": sql, "answer": f"SQL execution error: {e}"}

    answer = generate_answer(question, sql, columns, rows)
    return {"question": question, "sql": sql, "columns": columns, "rows": rows, "answer": answer}


if __name__ == "__main__":
    result = run_pipeline("Which region had higher total sales, North or South?")
    print(result["answer"])