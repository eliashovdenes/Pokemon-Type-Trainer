import sqlite3

def create_users_db():
    conn = sqlite3.connect('src/persons.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL 
        )
    ''')
    conn.commit()
    conn.close()

# Call this function once to create the database and table
create_users_db()


def create_user_scores_table():
    conn = sqlite3.connect('src/persons.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_scores (
            user_id INTEGER,
            highest_streak INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# Call this function once to create the table
create_user_scores_table()