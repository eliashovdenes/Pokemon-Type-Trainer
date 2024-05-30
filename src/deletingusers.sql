-- Replace 'username' with the actual username you want to delete
BEGIN;

-- Identify the user_id
WITH user_to_delete AS (
    SELECT user_id FROM users WHERE username = 'username'
)

-- Delete from user_scores
DELETE FROM user_scores WHERE user_id = (SELECT user_id FROM user_to_delete);

-- Delete from users
DELETE FROM users WHERE user_id = (SELECT user_id FROM user_to_delete);

COMMIT;