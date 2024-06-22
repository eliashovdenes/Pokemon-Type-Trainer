import os
import psycopg2
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def copy_table_data(sqlite_cursor, pg_conn, table_name):
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    columns = [desc[0] for desc in sqlite_cursor.description]

    # Create a string of %s for the values
    placeholders = ', '.join(['%s' for _ in columns])
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    pg_cursor = pg_conn.cursor()
    pg_cursor.executemany(insert_query, rows)
    pg_conn.commit()
    pg_cursor.close()

def main():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('./backup.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()

    # Ensure tables are created in PostgreSQL
    pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    );
    """)
    pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_scores (
        score_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        highest_streak INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
    );
    """)
    pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_daily_scores (
        daily_score_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        score_date DATE NOT NULL,
        daily_score INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
        UNIQUE (user_id, score_date)
    );
    """)
    pg_conn.commit()

    # Copy data from SQLite to PostgreSQL
    copy_table_data(sqlite_cursor, pg_conn, 'users')
    copy_table_data(sqlite_cursor, pg_conn, 'user_scores')
    copy_table_data(sqlite_cursor, pg_conn, 'user_daily_scores')

    # Close connections
    sqlite_cursor.close()
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    main()
