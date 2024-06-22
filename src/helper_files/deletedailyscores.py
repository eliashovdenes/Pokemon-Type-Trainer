import os
import psycopg2
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def delete_current_day_scores(pg_conn):
    pg_cursor = pg_conn.cursor()
    today_date = date.today()
    delete_query = "DELETE FROM user_daily_scores WHERE score_date = %s"
    pg_cursor.execute(delete_query, (today_date,))
    pg_conn.commit()
    pg_cursor.close()

def main():
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Delete today's scores
    delete_current_day_scores(pg_conn)

    # Close connection
    pg_conn.close()

if __name__ == "__main__":
    main()
