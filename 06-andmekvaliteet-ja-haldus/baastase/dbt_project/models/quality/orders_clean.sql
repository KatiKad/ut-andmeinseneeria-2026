-- Siia jäävad ainult read, mis läbisid kvaliteedikontrolli
-- ja millele leidsime õige dimensiooni versiooni.

SELECT
    b.staging_row_id,
    b.order_id_clean AS order_id,
    b.order_date,
    s.store_version_key,
    s.store_id,
    s.store_name,
    s.city,
    s.region,
    p.product_version_key,
    p.product_id,
    p.product_name,
    p.category,
    b.quantity,
    b.unit_price_eur,
    ROUND(b.quantity * b.unit_price_eur, 2) AS line_amount_eur,
    b.source_updated_at,
    b.loaded_at
FROM {{ ref('int_orders_base') }} AS b
INNER JOIN {{ ref('dim_stores_scd') }} AS s
    ON b.store_id_clean = s.store_id
   AND b.order_date BETWEEN s.valid_from AND s.valid_to
INNER JOIN {{ ref('dim_products_scd') }} AS p
    ON b.product_id_clean = p.product_id
   AND b.order_date BETWEEN p.valid_from AND p.valid_to
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ ref('order_rule_results') }} AS r
    WHERE r.staging_row_id = b.staging_row_id
)
