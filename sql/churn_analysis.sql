-- Marketing segmentation: prioritize high-value customers who have gone quiet.
-- Users with >30 days since last login and LTV > 50 are ideal for a re-activation journey.
-- This balances retention spend on customers likely to return if nudged.

SELECT
    id AS user_id,
    email,
    last_login AS last_login_date,
    total_spend
FROM users
WHERE
    DATE(last_login) < DATE('now', '-30 days')
    AND total_spend > 50.00
ORDER BY total_spend DESC, last_login_date ASC;
