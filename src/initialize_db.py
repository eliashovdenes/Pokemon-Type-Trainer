import psycopg2

# Set the DATABASE_URL directly
DATABASE_URL = "secret"

# SQL commands to create tables
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
"""

create_user_scores_table = """
CREATE TABLE IF NOT EXISTS user_scores (
    score_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    highest_streak INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
"""

def initialize_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(create_users_table)
    cur.execute(create_user_scores_table)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")