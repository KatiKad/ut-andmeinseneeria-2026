-- See fail võrdleb worker'i jooksvalt uuendatud live-koondit
-- sama andmestiku põhjal uuesti arvutatud pakktöötluse koondiga.

-- Pakktöötluse koond arvutatakse iga kord otsast peale.
\echo ''
\echo '== Tühjendan analytics.sales_summary_batch tabeli =='
TRUNCATE analytics.sales_summary_batch;

-- Ehita koond kõigist korrastatud tellimuse sündmustest.
\echo ''
\echo '== Ehitan analytics.sales_summary_batch pakktöötluse koondi =='
INSERT INTO analytics.sales_summary_batch (
    store_id,
    product_id,
    order_count,
    total_quantity,
    total_amount_eur
)
SELECT
    store_id,
    product_id,
    COUNT(*) AS order_count,
    SUM(quantity) AS total_quantity,
    SUM(total_amount_eur) AS total_amount_eur
FROM analytics.order_events
GROUP BY store_id, product_id;

-- Võrdle live-koondi ja pakktöötluse arve ridade kaupa.
-- `OK` tähendab, et kordustöötlus ei ole koondit topelt kasvatanud.
\echo ''
\echo '== analytics.sales_summary_live vs analytics.sales_summary_batch: koondite võrdlus =='
SELECT
    COALESCE(live.store_id, batch.store_id) AS store_id,
    COALESCE(live.product_id, batch.product_id) AS product_id,
    live.order_count AS live_order_count,
    batch.order_count AS batch_order_count,
    live.total_quantity AS live_total_quantity,
    batch.total_quantity AS batch_total_quantity,
    live.total_amount_eur AS live_total_amount_eur,
    batch.total_amount_eur AS batch_total_amount_eur,
    CASE
        WHEN live.order_count = batch.order_count
            AND live.total_quantity = batch.total_quantity
            AND live.total_amount_eur = batch.total_amount_eur
        THEN 'OK'
        ELSE 'ERINEB'
    END AS comparison_result
FROM analytics.sales_summary_live AS live
FULL OUTER JOIN analytics.sales_summary_batch AS batch
    ON live.store_id = batch.store_id
    AND live.product_id = batch.product_id
ORDER BY store_id, product_id;
