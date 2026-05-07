-- Ühtlustame tellimuste toorread.
-- Tühjad tekstiväljad muudame NULL-ideks, et kvaliteedireegleid oleks lihtsam kirjutada.

SELECT
    staging_row_id,
    NULLIF(TRIM(order_id), '') AS order_id_clean,
    order_id,
    order_date,
    NULLIF(TRIM(store_id), '') AS store_id_clean,
    NULLIF(TRIM(product_id), '') AS product_id_clean,
    store_id,
    product_id,
    quantity,
    unit_price_eur,
    source_updated_at,
    loaded_at
FROM {{ source('staging', 'orders_raw') }}
