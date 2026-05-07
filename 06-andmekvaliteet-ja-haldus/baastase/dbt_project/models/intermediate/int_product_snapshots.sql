-- Puhastame toodete kuised snapshotid ühtlaseks lähtekujuks.
-- See mudel on esimene samm allika ja SCD dimensiooni vahel.

SELECT
    snapshot_month,
    TRIM(product_id) AS product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    base_price_eur,
    loaded_at,
    TRIM(product_id) || ':' || TO_CHAR(snapshot_month, 'YYYY-MM-DD') AS product_snapshot_key
FROM {{ source('staging', 'product_snapshots_raw') }}
