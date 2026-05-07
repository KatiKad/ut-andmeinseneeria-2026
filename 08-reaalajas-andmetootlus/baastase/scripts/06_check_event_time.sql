-- See fail aitab võrrelda sündmuse aega ja töötluse aega.
-- `event_time` on näite äriaeg. `processed_at` näitab, millal worker sündmuse töötles.

\pset null '(puudub)'

\echo ''
\echo '== stream.event_log: sündmuse aeg ja töötluse aeg =='
SELECT
    event_id,
    event_time,
    published_at,
    processed_at,
    processed_at - event_time AS total_delay
FROM stream.event_log
ORDER BY published_at DESC
LIMIT 5;
