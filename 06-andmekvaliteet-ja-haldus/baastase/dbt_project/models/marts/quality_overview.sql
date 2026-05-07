-- Lühike näitaja sellest, kui suur osa tooridadest jäi kvaliteedisõelale ette.

WITH counts AS (
    SELECT
        (SELECT COUNT(*) FROM {{ source('staging', 'orders_raw') }}) AS raw_order_rows,
        (SELECT COUNT(*) FROM {{ ref('orders_clean') }}) AS clean_order_rows,
        (
            SELECT COUNT(DISTINCT staging_row_id)
            FROM {{ ref('order_rule_results') }}
        ) AS rejected_row_count,
        (SELECT COUNT(*) FROM {{ ref('order_rule_results') }}) AS total_rule_failures
)
SELECT
    raw_order_rows,
    clean_order_rows,
    rejected_row_count,
    total_rule_failures,
    ROUND(
        100.0 * rejected_row_count / NULLIF(raw_order_rows, 0),
        2
    ) AS rejected_row_percent,
    NOW() AS refreshed_at
FROM counts
