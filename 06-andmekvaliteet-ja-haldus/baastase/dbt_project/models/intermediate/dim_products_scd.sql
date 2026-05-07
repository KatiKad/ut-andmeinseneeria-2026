{{ config(materialized='table') }}

-- Ehitame toodete SCD Type 2 dimensiooni.
-- Iga muudatuse hetkest alates tekib uus kehtivusvahemik.

WITH ordered_snapshots AS (
    SELECT
        product_id,
        product_name,
        category,
        base_price_eur,
        snapshot_month AS valid_from,
        LEAD(snapshot_month) OVER (
            PARTITION BY product_id
            ORDER BY snapshot_month
        ) AS next_valid_from
    FROM {{ ref('int_product_snapshots') }}
)
SELECT
    product_id || ':' || TO_CHAR(valid_from, 'YYYY-MM-DD') AS product_version_key,
    product_id,
    product_name,
    category,
    base_price_eur,
    valid_from,
    COALESCE(next_valid_from - 1, DATE '9999-12-31') AS valid_to,
    next_valid_from IS NULL AS is_current
FROM ordered_snapshots
