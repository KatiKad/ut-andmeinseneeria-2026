TRUNCATE TABLE staging.user_status;

\copy staging.user_status (email, account_status, source_system, updated_at) FROM '/data/kasutaja_staatus.csv' WITH (FORMAT csv, HEADER true);
