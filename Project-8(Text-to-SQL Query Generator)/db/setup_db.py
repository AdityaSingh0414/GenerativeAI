import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sample.db")

def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)  # start fresh each time

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- Table 1: students ---
    cur.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER,
            city TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO students (name, grade, city) VALUES (?, ?, ?)",
        [
            ("Aarav Sharma", 10, "Delhi"),
            ("Priya Singh", 9, "Mumbai"),
            ("Rohan Mehta", 10, "Delhi"),
            ("Ananya Gupta", 8, "Bangalore"),
        ],
    )

    # --- Table 2: sales ---
    cur.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT,
            amount REAL,
            region TEXT,
            sale_date TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO sales (product, amount, region, sale_date) VALUES (?, ?, ?, ?)",
        [
            ("Laptop", 55000, "North", "2024-01-15"),
            ("Phone", 20000, "South", "2024-02-10"),
            ("Laptop", 58000, "South", "2024-03-05"),
            ("Tablet", 15000, "North", "2024-03-20"),
        ],
    )

    # --- Table 3: ipl_matches ---
    cur.execute("""
        CREATE TABLE ipl_matches (
            id INTEGER PRIMARY KEY,
            season INTEGER,
            team1 TEXT,
            team2 TEXT,
            winner TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO ipl_matches (season, team1, team2, winner) VALUES (?, ?, ?, ?)",
        [
            (2019, "Mumbai Indians", "Chennai Super Kings", "Mumbai Indians"),
            (2019, "Delhi Capitals", "Kolkata Knight Riders", "Delhi Capitals"),
            (2019, "Mumbai Indians", "Sunrisers Hyderabad", "Mumbai Indians"),
        ],
    )

    conn.commit()
    conn.close()
    print(f"✅ Database created at {DB_PATH}")

if __name__ == "__main__":
    create_database()