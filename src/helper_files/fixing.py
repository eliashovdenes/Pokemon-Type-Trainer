import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def reset_user_daily_scores_table(pg_conn):
    pg_cursor = pg_conn.cursor()

    # Drop the existing user_daily_scores table
    drop_table_query = "DROP TABLE IF EXISTS user_daily_scores;"
    pg_cursor.execute(drop_table_query)
    
    # Recreate the user_daily_scores table with the original structure
    create_user_daily_scores_table = """
    CREATE TABLE IF NOT EXISTS user_daily_scores (
        daily_score_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        score_date DATE NOT NULL,
        daily_score INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
        UNIQUE (user_id, score_date)  -- Ensure one score per user per day
    );
    """
    pg_cursor.execute(create_user_daily_scores_table)
    
    pg_conn.commit()
    pg_cursor.close()

def main():
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Reset the user_daily_scores table
    reset_user_daily_scores_table(pg_conn)

    # Close connection
    pg_conn.close()

if __name__ == "__main__":
    main()
