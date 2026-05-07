-- Ühes kuus peab sama toode esinema ainult ühe korra.

SELECT
    snapshot_month,
    product_id,
    COUNT(*) AS row_count
FROM {{ source('staging', 'product_snapshots_raw') }}
GROUP BY snapshot_month, product_id
HAVING COUNT(*) > 1
