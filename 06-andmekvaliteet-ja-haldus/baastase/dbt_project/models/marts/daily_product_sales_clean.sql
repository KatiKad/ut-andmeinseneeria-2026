-- Ehita analüütikakiht ainult puhastest ridadest.
-- See on sama mõte nagu põhiraja analytics.daily_product_sales_clean tabelil.

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
FROM {{ ref('orders_clean') }}
GROUP BY
    order_date,
    store_id,
    store_name,
    region,
    product_id,
    product_name,
    category
