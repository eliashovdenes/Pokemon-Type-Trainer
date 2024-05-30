-- Delete from user_scores
DELETE FROM user_scores WHERE user_id = (SELECT user_id FROM user_to_delete);

-- Delete from users
DELETE FROM users WHERE user_id = (SELECT user_id FROM user_to_delete);
