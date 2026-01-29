import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/logements.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            prix INTEGER,
            surface REAL,
            prix_m2 REAL,
            type_bien TEXT,
            ville TEXT,
            site_source TEXT,
            image TEXT,
            url TEXT,
            date_scraping TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()