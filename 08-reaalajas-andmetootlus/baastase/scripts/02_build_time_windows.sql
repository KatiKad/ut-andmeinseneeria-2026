-- See fail ehitab kaks 5 minuti akna põhist koondit:
-- üks sündmuse aja ja teine töötluse aja järgi.
-- Nii saab näha, miks hilinenud sündmus võib valesse aknasse sattuda.

-- Ehitus on korduskäivitatav: kustutame eelmise tulemuse ja arvutame uuesti.
\echo ''
\echo '== Tühjendan eelmised akende koondid =='
TRUNCATE analytics.sales_windows_event_time;
TRUNCATE analytics.sales_windows_processing_time;

-- Koond sündmuse aja järgi. See vastab tavaliselt ärilisele küsimusele:
-- "Millal tellimus tegelikult juhtus?"
\echo ''
\echo '== Ehitan analytics.sales_windows_event_time koondi sündmuse aja järgi =='
INSERT INTO analytics.sales_windows_event_time (
    window_start,
    window_end,
    store_id,
    order_count,
    total_amount_eur
)
SELECT
    date_bin('5 minutes', event_time, TIMESTAMPTZ '2026-01-01 00:00:00+00') AS window_start,
    date_bin('5 minutes', event_time, TIMESTAMPTZ '2026-01-01 00:00:00+00') + INTERVAL '5 minutes' AS window_end,
    store_id,
    COUNT(*) AS order_count,
    SUM(total_amount_eur) AS total_amount_eur
FROM analytics.order_events
GROUP BY window_start, window_end, store_id;

-- Koond töötluse aja järgi. See näitab, millal meie süsteem sündmuse käsitles.
\echo ''
\echo '== Ehitan analytics.sales_windows_processing_time koondi töötluse aja järgi =='
INSERT INTO analytics.sales_windows_processing_time (
    window_start,
    window_end,
    store_id,
    order_count,
    total_amount_eur
)
SELECT
    date_bin('5 minutes', processed_at, TIMESTAMPTZ '2026-01-01 00:00:00+00') AS window_start,
    date_bin('5 minutes', processed_at, TIMESTAMPTZ '2026-01-01 00:00:00+00') + INTERVAL '5 minutes' AS window_end,
    store_id,
    COUNT(*) AS order_count,
    SUM(total_amount_eur) AS total_amount_eur
FROM analytics.order_events
GROUP BY window_start, window_end, store_id;

-- Märgime üle kahe minuti hilinenud sündmused eraldi tabelisse.
-- See on lihtne õppereegel, mitte täismahus voogtöötluse vesimärk.
\echo ''
\echo '== Märgin hilinenud sündmused tabelisse staging.late_events =='
INSERT INTO staging.late_events (
    event_id,
    event_time,
    processed_at,
    delay_seconds,
    note
)
SELECT
    event_id,
    event_time,
    processed_at,
    EXTRACT(EPOCH FROM (processed_at - event_time))::NUMERIC(12, 2) AS delay_seconds,
    'Näide: sündmus hilines üle kahe minuti. Praktikumis märgime selle nähtavaks, aga ei ehita täismahus vesimärgi mootorit.' AS note
FROM analytics.order_events
WHERE processed_at - event_time > INTERVAL '2 minutes'
ON CONFLICT (event_id) DO UPDATE
SET
    processed_at = EXCLUDED.processed_at,
    delay_seconds = EXCLUDED.delay_seconds,
    recorded_at = now();

-- Kuva mõlemad koondid ühes väljundis.
\echo ''
\echo '== analytics.sales_windows_event_time ja analytics.sales_windows_processing_time: võrdlus =='
SELECT
    'event_time' AS window_basis,
    window_start,
    window_end,
    store_id,
    order_count,
    total_amount_eur
FROM analytics.sales_windows_event_time
UNION ALL
SELECT
    'processing_time' AS window_basis,
    window_start,
    window_end,
    store_id,
    order_count,
    total_amount_eur
FROM analytics.sales_windows_processing_time
ORDER BY window_start, window_basis, store_id;

-- Kuva hilinenud sündmused, kui neid tekkis.
\echo ''
\echo '== staging.late_events: hilinenud sündmused =='
SELECT
    event_id,
    event_time,
    processed_at,
    delay_seconds,
    note
FROM staging.late_events
ORDER BY delay_seconds DESC;
