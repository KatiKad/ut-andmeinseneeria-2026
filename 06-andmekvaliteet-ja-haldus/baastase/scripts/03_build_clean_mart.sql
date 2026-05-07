-- Ehita analüütikakiht ainult puhastest ridadest.
--
-- Selle sammu mõte on näidata, et raporti alusandmed ei tule otse staging-kihist.
-- Enne läheb vahele kvaliteedikontroll.

DROP TABLE IF EXISTS analytics.daily_product_sales_clean;
DROP TABLE IF EXISTS analytics.quality_overview;

CREATE TABLE analytics.daily_product_sales_clean AS
SELECT
    order_date AS sales_date,
    store_id,
    store_name,
    region,
    product_id,
    product_name,
    category,
    COUNT(*) AS order_count,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(line_amount_eur), 2) AS gross_sales_eur,
    MIN(source_updated_at) AS first_source_updated_at,
    MAX(source_updated_at) AS last_source_updated_at,
    NOW() AS built_at
FROM quality.orders_clean
GROUP BY
    order_date,
    store_id,
    store_name,
    region,
    product_id,
    product_name,
    category;

ALTER TABLE analytics.daily_product_sales_clean
    ADD PRIMARY KEY (sales_date, store_id, product_id);

CREATE TABLE analytics.quality_overview AS
WITH counts AS (
    SELECT
        (SELECT COUNT(*) FROM staging.orders_raw) AS raw_order_rows,
        (SELECT COUNT(*) FROM quality.orders_clean) AS clean_order_rows,
        (SELECT COUNT(DISTINCT staging_row_id) FROM quality.order_rule_results) AS rejected_row_count,
        (SELECT COUNT(*) FROM quality.order_rule_results) AS total_rule_failures
)
SELECT
    raw_order_rows,
    clean_order_rows,
    rejected_row_count,
    total_rule_failures,
    ROUND(
        100.0 * rejected_row_count / NULLIF(raw_order_rows, 0),
        2
    ) AS rejected_row_percent,
    NOW() AS refreshed_at
FROM counts;
