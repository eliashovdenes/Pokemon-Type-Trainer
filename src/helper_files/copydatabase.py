import os
import psycopg2
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# SQL commands to create tables in SQLite
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
"""

create_user_scores_table = """
CREATE TABLE IF NOT EXISTS user_scores (
    score_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    highest_streak INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
"""

create_user_daily_scores_table = """
CREATE TABLE IF NOT EXISTS user_daily_scores (
    daily_score_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score_date DATE NOT NULL,
    daily_score INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    UNIQUE (user_id, score_date)
);
"""

def copy_table_data(pg_cursor, sqlite_conn, table_name):
    pg_cursor.execute(f"SELECT * FROM {table_name}")
    rows = pg_cursor.fetchall()
    columns = [desc[0] for desc in pg_cursor.description]

    # Create a string of question marks for the values
    placeholders = ', '.join(['?' for _ in columns])
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.executemany(insert_query, rows)
    sqlite_conn.commit()

def main():
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()

    # Connect to SQLite
    sqlite_conn = sqlite3.connect('backup.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Create tables in SQLite
    sqlite_cursor.execute(create_users_table)
    sqlite_cursor.execute(create_user_scores_table)
    sqlite_cursor.execute(create_user_daily_scores_table)
    sqlite_conn.commit()

    # Copy data from PostgreSQL to SQLite
    copy_table_data(pg_cursor, sqlite_conn, 'users')
    copy_table_data(pg_cursor, sqlite_conn, 'user_scores')
    copy_table_data(pg_cursor, sqlite_conn, 'user_daily_scores')

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()

if __name__ == "__main__":
    main()
