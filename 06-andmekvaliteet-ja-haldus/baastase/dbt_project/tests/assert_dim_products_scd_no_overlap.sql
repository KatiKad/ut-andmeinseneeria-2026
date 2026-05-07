-- Sama toote kehtivusvahemikud ei tohi ajaliselt kattuda.

WITH ranges AS (
    SELECT
        product_id,
        valid_from,
        valid_to,
        LEAD(valid_from) OVER (
            PARTITION BY product_id
            ORDER BY valid_from
        ) AS next_valid_from
    FROM {{ ref('dim_products_scd') }}
)
SELECT
    product_id,
    valid_from,
    valid_to,
    next_valid_from
FROM ranges
WHERE next_valid_from IS NOT NULL
  AND valid_to >= next_valid_from
