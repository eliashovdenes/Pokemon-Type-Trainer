import sqlite3

def delete_user(username):
    conn = sqlite3.connect('src/persons.db')
    c = conn.cursor()
    
    # Fetch the user ID
    c.execute('SELECT user_id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if user:
        user_id = user[0]
        # Delete related data from user_scores table
        c.execute('DELETE FROM user_scores WHERE user_id = ?', (user_id,))
        # Delete the user from users table
        c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        print(f"User '{username}' and all related data deleted successfully!")
    else:
        conn.close()
        print("User not found.")

# Example usage
username_to_delete = input("Enter the username to delete: ").strip()
if username_to_delete:
    delete_user(username_to_delete)
else:
    print("Username cannot be empty.")