SELECT COUNT(*) AS rows_in_user_status
FROM staging.user_status;

SELECT email, account_status, source_system, updated_at
FROM staging.user_status
ORDER BY updated_at, email;
