-- See fail tühjendab praktikumi tabelid, kuid ei peata konteinereid.
-- Kasuta seda siis, kui tahad sama keskkonnaga uuesti algusest alustada.

\echo ''
\echo '== Tühjendan praktikumi tabelid ja lähtestan loendurid =='
TRUNCATE
    stream.task_dispatch_log,
    stream.event_log,
    staging.bad_events,
    staging.late_events,
    analytics.order_events,
    analytics.sales_summary_live,
    analytics.sales_windows_event_time,
    analytics.sales_windows_processing_time,
    analytics.sales_summary_batch,
    monitoring.worker_task_log
RESTART IDENTITY;
