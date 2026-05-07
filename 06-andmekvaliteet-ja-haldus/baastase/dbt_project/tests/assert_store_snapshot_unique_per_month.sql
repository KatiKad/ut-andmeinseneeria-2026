-- Ühes kuus peab sama pood esinema ainult ühe korra.

SELECT
    snapshot_month,
    store_id,
    COUNT(*) AS row_count
FROM {{ source('staging', 'store_snapshots_raw') }}
GROUP BY snapshot_month, store_id
HAVING COUNT(*) > 1
