-- See fail kontrollib, kas sama sündmuse korduv järjekorda saatmine oli ohutu.
-- Eesmärk on näha, et järjekorda saatmise logis võib olla kordus,
-- kuid analüütika sündmuste tabelisse ei teki topeltrida.

\pset null '(puudub)'

-- Sama sündmus võib olla Celery järjekorda saadetud rohkem kui üks kord.
\echo ''
\echo '== stream.task_dispatch_log: korduvad järjekorda saatmised =='
SELECT
    event_id,
    COUNT(*) AS dispatch_count
FROM stream.task_dispatch_log
GROUP BY event_id
HAVING COUNT(*) > 1
ORDER BY dispatch_count DESC, event_id;

-- Korrastatud sündmuste tabelis ei tohi sama event_id mitu korda esineda.
\echo ''
\echo '== analytics.order_events: topeltridade kontroll event_id järgi =='
SELECT
    event_id,
    COUNT(*) AS rows_per_event
FROM analytics.order_events
GROUP BY event_id
HAVING COUNT(*) > 1
ORDER BY rows_per_event DESC, event_id;

-- Worker'i logis peaks korduva töötluse puhul nägema skipped olekut.
\echo ''
\echo '== monitoring.worker_task_log: viimased 10 workeri töötluskatset =='
SELECT
    task_log_id,
    event_id,
    status,
    message,
    started_at,
    finished_at
FROM monitoring.worker_task_log
ORDER BY task_log_id DESC
LIMIT 10;
