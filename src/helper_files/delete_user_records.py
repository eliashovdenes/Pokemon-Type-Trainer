import psycopg2
from getpass import getpass
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def delete_user_records(username):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        # Fetch the user_id for the given username
        cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
        user_id = cur.fetchone()
        
        if user_id:
            user_id = user_id[0]
            # Delete records from user_scores table
            cur.execute("DELETE FROM user_scores WHERE user_id = %s;", (user_id,))
            
            # Delete records from user_daily_scores table
            cur.execute("DELETE FROM user_daily_scores WHERE user_id = %s;", (user_id,))
            
            # Delete the user from users table
            cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
            
            # Commit the transaction
            conn.commit()
            print(f"All records for username '{username}' have been deleted.")
        else:
            print(f"No user found with username '{username}'.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    username = input("Enter the username to delete: ")
    delete_user_records(username)
