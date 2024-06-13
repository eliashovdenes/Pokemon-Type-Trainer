import psycopg2
from getpass import getpass
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def update_highest_streak(username, new_score):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        # Fetch the user_id for the given username
        cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
        user_id = cur.fetchone()
        
        if user_id:
            user_id = user_id[0]
            # Update the score in the highest_streak_leaderboard table
            cur.execute("UPDATE user_scores SET highest_streak = %s WHERE user_id = %s;", (new_score, user_id))
            
            # Commit the transaction
            conn.commit()
            print(f"The score for username '{username}' has been updated to {new_score}.")
        else:
            print(f"No user found with username '{username}'.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    username = input("Enter the username to update: ")
    new_score = input("Enter the new score: ")
    
    # Ensure the new score is an integer
    try:
        new_score = int(new_score)
        update_highest_streak(username, new_score)
    except ValueError:
        print("Invalid score. Please enter an integer value.")
