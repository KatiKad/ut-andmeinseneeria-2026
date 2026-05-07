-- Puhastame poodide kuised snapshotid samal põhimõttel nagu toodete puhul.

SELECT
    snapshot_month,
    TRIM(store_id) AS store_id,
    TRIM(store_name) AS store_name,
    TRIM(city) AS city,
    TRIM(region) AS region,
    loaded_at,
    TRIM(store_id) || ':' || TO_CHAR(snapshot_month, 'YYYY-MM-DD') AS store_snapshot_key
FROM {{ source('staging', 'store_snapshots_raw') }}
