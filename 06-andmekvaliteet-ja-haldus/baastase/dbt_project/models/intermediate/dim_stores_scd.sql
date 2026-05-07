{{ config(materialized='table') }}

-- Ehitame poodide SCD Type 2 dimensiooni.
-- Sama poe kohta võib olla mitu ajaloolist versiooni.

WITH ordered_snapshots AS (
    SELECT
        store_id,
        store_name,
        city,
        region,
        snapshot_month AS valid_from,
        LEAD(snapshot_month) OVER (
            PARTITION BY store_id
            ORDER BY snapshot_month
        ) AS next_valid_from
    FROM {{ ref('int_store_snapshots') }}
)
SELECT
    store_id || ':' || TO_CHAR(valid_from, 'YYYY-MM-DD') AS store_version_key,
    store_id,
    store_name,
    city,
    region,
    valid_from,
    COALESCE(next_valid_from - 1, DATE '9999-12-31') AS valid_to,
    next_valid_from IS NULL AS is_current
FROM ordered_snapshots
