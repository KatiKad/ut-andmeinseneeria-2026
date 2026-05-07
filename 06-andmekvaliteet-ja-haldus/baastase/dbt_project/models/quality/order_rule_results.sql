-- Koondame peamiste kvaliteedireeglite rikkumised ühte mudelisse.
-- Üks rida selles tabelis tähendab üht konkreetset reeglirikkumist.

WITH duplicate_order_ids AS (
    SELECT order_id_clean
    FROM {{ ref('int_orders_base') }}
    WHERE order_id_clean IS NOT NULL
    GROUP BY order_id_clean
    HAVING COUNT(*) > 1
),
product_match AS (
    SELECT
        b.staging_row_id,
        p.product_version_key,
        p.base_price_eur
    FROM {{ ref('int_orders_base') }} AS b
    LEFT JOIN {{ ref('dim_products_scd') }} AS p
        ON b.product_id_clean = p.product_id
       AND b.order_date BETWEEN p.valid_from AND p.valid_to
),
store_match AS (
    SELECT
        b.staging_row_id,
        s.store_version_key
    FROM {{ ref('int_orders_base') }} AS b
    LEFT JOIN {{ ref('dim_stores_scd') }} AS s
        ON b.store_id_clean = s.store_id
       AND b.order_date BETWEEN s.valid_from AND s.valid_to
)
SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'order_id_missing' AS rule_name,
    'Tellimuse ID puudub.' AS issue_message,
    COALESCE(b.order_id, '<NULL>') AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
WHERE b.order_id_clean IS NULL

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'order_id_duplicate' AS rule_name,
    'Sama tellimuse ID esineb rohkem kui üks kord.' AS issue_message,
    b.order_id AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
INNER JOIN duplicate_order_ids AS d
    ON b.order_id_clean = d.order_id_clean

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'store_id_missing' AS rule_name,
    'Poe ID puudub.' AS issue_message,
    COALESCE(b.store_id, '<NULL>') AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
WHERE b.store_id_clean IS NULL

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'product_id_missing' AS rule_name,
    'Toote ID puudub.' AS issue_message,
    COALESCE(b.product_id, '<NULL>') AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
WHERE b.product_id_clean IS NULL

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'quantity_must_be_positive' AS rule_name,
    'Kogus peab olema nullist suurem.' AS issue_message,
    COALESCE(b.quantity::text, '<NULL>') AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
WHERE b.quantity IS NULL OR b.quantity <= 0

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'store_must_exist_for_order_date' AS rule_name,
    'Tellimuse kuupäeva jaoks ei leitud sobivat poe versiooni.' AS issue_message,
    b.store_id AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
LEFT JOIN store_match AS s
    ON b.staging_row_id = s.staging_row_id
WHERE b.store_id_clean IS NOT NULL
  AND s.store_version_key IS NULL

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'product_must_exist_for_order_date' AS rule_name,
    'Tellimuse kuupäeva jaoks ei leitud sobivat toote versiooni.' AS issue_message,
    b.product_id AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
LEFT JOIN product_match AS p
    ON b.staging_row_id = p.staging_row_id
WHERE b.product_id_clean IS NOT NULL
  AND p.product_version_key IS NULL

UNION ALL

SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    'unit_price_close_to_snapshot' AS rule_name,
    'Tellimuse ühikuhind erineb liiga palju sama perioodi snapshot-hinnast.' AS issue_message,
    COALESCE(b.unit_price_eur::text, '<NULL>') AS failed_value,
    NOW() AS checked_at
FROM {{ ref('int_orders_base') }} AS b
INNER JOIN product_match AS p
    ON b.staging_row_id = p.staging_row_id
WHERE p.product_version_key IS NOT NULL
  AND (
      b.unit_price_eur IS NULL
      OR b.unit_price_eur NOT BETWEEN p.base_price_eur - 2.00 AND p.base_price_eur + 2.00
  )
