-- Käivita peamised andmekvaliteedi kontrollid.
--
-- Tulemus jaguneb kolmeks:
-- 1. detailne vigade tabel `quality.order_rule_results`
-- 2. lühike koond `quality.order_issue_summary`
-- 3. puhas väljund `quality.orders_clean`

DROP TABLE IF EXISTS quality.order_rule_results;
DROP TABLE IF EXISTS quality.order_issue_summary;
DROP TABLE IF EXISTS quality.orders_clean;

CREATE TABLE quality.order_rule_results AS
WITH base_orders AS (
    -- Teeme toorandmetest ühtlasema lähtekuju.
    -- Näiteks tühjad tekstid muudame siin `NULL` väärtusteks,
    -- et puuduvate väljade kontrollid oleksid lihtsamad.
    SELECT
        o.staging_row_id,
        NULLIF(TRIM(o.order_id), '') AS order_id_clean,
        o.order_id,
        o.order_date,
        NULLIF(TRIM(o.store_id), '') AS store_id_clean,
        NULLIF(TRIM(o.product_id), '') AS product_id_clean,
        o.store_id,
        o.product_id,
        o.quantity,
        o.unit_price_eur
    FROM staging.orders_raw AS o
),
duplicate_order_ids AS (
    -- Leiame tellimuse ID-d, mis esinevad rohkem kui üks kord.
    SELECT order_id_clean
    FROM base_orders
    WHERE order_id_clean IS NOT NULL
    GROUP BY order_id_clean
    HAVING COUNT(*) > 1
),
product_match AS (
    -- Proovime iga tellimuse siduda just selle tooteversiooniga,
    -- mis oli tellimuse kuupäeval kehtiv.
    SELECT
        b.staging_row_id,
        p.product_version_key,
        p.base_price_eur
    FROM base_orders AS b
    LEFT JOIN intermediate.dim_products_scd AS p
        ON b.product_id_clean = p.product_id
       AND b.order_date BETWEEN p.valid_from AND p.valid_to
),
store_match AS (
    -- Sama sidumine poe dimensiooniga.
    SELECT
        b.staging_row_id,
        s.store_version_key
    FROM base_orders AS b
    LEFT JOIN intermediate.dim_stores_scd AS s
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
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
FROM base_orders AS b
INNER JOIN product_match AS p
    ON b.staging_row_id = p.staging_row_id
WHERE p.product_version_key IS NOT NULL
  AND (
      b.unit_price_eur IS NULL
      OR b.unit_price_eur NOT BETWEEN p.base_price_eur - 2.00 AND p.base_price_eur + 2.00
  );

CREATE INDEX idx_order_rule_results_row
    ON quality.order_rule_results (staging_row_id);

CREATE INDEX idx_order_rule_results_rule
    ON quality.order_rule_results (rule_name);

CREATE TABLE quality.order_issue_summary AS
-- Koondame detailse veatabeli lühikeseks kokkuvõtteks,
-- et õppijal oleks lihtsam näha, millised reeglid kõige rohkem ridu mõjutavad.
SELECT
    rule_name,
    COUNT(*) AS failed_rows
FROM quality.order_rule_results
GROUP BY rule_name
ORDER BY failed_rows DESC, rule_name;

CREATE TABLE quality.orders_clean AS
WITH base_orders AS (
    -- Alustame samast ühtlustatud lähtekujust nagu veakontrollis.
    SELECT
        o.staging_row_id,
        NULLIF(TRIM(o.order_id), '') AS order_id,
        o.order_date,
        NULLIF(TRIM(o.store_id), '') AS store_id,
        NULLIF(TRIM(o.product_id), '') AS product_id,
        o.quantity,
        o.unit_price_eur,
        o.source_updated_at,
        o.loaded_at
    FROM staging.orders_raw AS o
)
SELECT
    b.staging_row_id,
    b.order_id,
    b.order_date,
    s.store_version_key,
    s.store_id,
    s.store_name,
    s.city,
    s.region,
    p.product_version_key,
    p.product_id,
    p.product_name,
    p.category,
    b.quantity,
    b.unit_price_eur,
    ROUND(b.quantity * b.unit_price_eur, 2) AS line_amount_eur,
    b.source_updated_at,
    b.loaded_at
FROM base_orders AS b
INNER JOIN intermediate.dim_stores_scd AS s
    ON b.store_id = s.store_id
   AND b.order_date BETWEEN s.valid_from AND s.valid_to
INNER JOIN intermediate.dim_products_scd AS p
    ON b.product_id = p.product_id
   AND b.order_date BETWEEN p.valid_from AND p.valid_to
-- Siia jäävad ainult read, mille kohta ei leitud ühtegi kvaliteediviga.
WHERE NOT EXISTS (
    SELECT 1
    FROM quality.order_rule_results AS r
    WHERE r.staging_row_id = b.staging_row_id
);

CREATE INDEX idx_orders_clean_order_date
    ON quality.orders_clean (order_date);
