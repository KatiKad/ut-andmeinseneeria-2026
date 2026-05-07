-- Päevase müügikoondi loomulik võti peab olema unikaalne.

SELECT
    sales_date,
    store_id,
    product_id,
    COUNT(*) AS row_count
FROM {{ ref('daily_product_sales_clean') }}
GROUP BY sales_date, store_id, product_id
HAVING COUNT(*) > 1
