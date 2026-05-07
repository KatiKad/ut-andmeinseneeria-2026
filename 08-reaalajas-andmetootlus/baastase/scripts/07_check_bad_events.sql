-- See fail kuvab viimased vigased sündmused.
-- Seda kasutatakse pärast `--include-bad-event` käsu käivitamist.

\pset null '(puudub)'

\echo ''
\echo '== staging.bad_events: viimased vigased sündmused =='
SELECT
    event_id,
    error_message,
    recorded_at
FROM staging.bad_events
ORDER BY recorded_at DESC
LIMIT 5;
