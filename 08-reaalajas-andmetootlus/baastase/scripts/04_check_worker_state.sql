-- See fail vaatab worker'i ja järjekorda saatmise olekut kokkuvõtlikult.

-- Sündmuste olekud sündmuste logis.
\echo ''
\echo '== stream.event_log: sündmuste arv oleku järgi =='
SELECT
    status,
    COUNT(*) AS events
FROM stream.event_log
GROUP BY status
ORDER BY status;

-- Mitu esmast ja korduvat saatmist Celery järjekorda on toimunud?
\echo ''
\echo '== stream.task_dispatch_log: saatmiste arv tüübi järgi =='
SELECT
    dispatch_kind,
    COUNT(*) AS tasks_sent
FROM stream.task_dispatch_log
GROUP BY dispatch_kind
ORDER BY dispatch_kind;

-- Worker'i logiridade koond oleku järgi.
\echo ''
\echo '== monitoring.worker_task_log: workeri logiridade arv oleku järgi =='
SELECT
    status,
    COUNT(*) AS worker_log_rows
FROM monitoring.worker_task_log
GROUP BY status
ORDER BY status;

-- Jooksvalt uuenev müügikoond, mille worker täidab.
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
ORDER BY last_event_time DESC
LIMIT 20;

-- Viimased worker'i töötluskatsed.
\echo ''
\echo '== monitoring.worker_task_log: viimased 20 workeri töötluskatset =='
SELECT
    task_log_id,
    event_id,
    status,
    message,
    started_at,
    finished_at,
    duration_ms
FROM monitoring.worker_task_log
ORDER BY task_log_id DESC
LIMIT 20;
