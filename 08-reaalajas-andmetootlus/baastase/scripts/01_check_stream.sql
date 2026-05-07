-- See fail koondab reaalajalähedase töövoo peamised kontrollpäringud.
-- Käivita seda pärast sündmuste avaldamist või worker'i taaskäivitamist.

\pset null '(puudub)'

-- Mitu sündmust on igas olekus?
\echo ''
\echo '== stream.event_log: sündmuste arv oleku järgi =='
SELECT
    status,
    COUNT(*) AS events
FROM stream.event_log
GROUP BY status
ORDER BY status;

-- Mitu korda on sündmuseid Celery järjekorda saadetud?
\echo ''
\echo '== stream.task_dispatch_log: järjekorda saadetud tööülesannete arv =='
SELECT
    COUNT(*) AS dispatched_tasks
FROM stream.task_dispatch_log;

-- Viimased sündmused koos avaldamise, järjekorda saatmise ja töötluse ajaga.
\echo ''
\echo '== stream.event_log: viimased 10 sündmust =='
SELECT
    event_id,
    event_type,
    event_time,
    published_at,
    queued_at,
    processed_at,
    status,
    celery_task_id,
    error_message
FROM stream.event_log
ORDER BY published_at DESC
LIMIT 10;

-- Jooksvalt uuenev müügikoond poe ja toote kaupa.
\echo ''
\echo '== analytics.sales_summary_live: live-koond poe ja toote kaupa =='
SELECT
    store_id,
    product_id,
    order_count,
    total_quantity,
    total_amount_eur,
    last_event_time,
    updated_at
FROM analytics.sales_summary_live
ORDER BY store_id, product_id
LIMIT 20;

-- Viimased worker'i töötluskatsed.
\echo ''
\echo '== monitoring.worker_task_log: viimased 10 workeri töötluskatset =='
SELECT
    task_log_id,
    celery_task_id,
    event_id,
    status,
    message,
    started_at,
    finished_at,
    duration_ms
FROM monitoring.worker_task_log
ORDER BY task_log_id DESC
LIMIT 10;
