-- Laeme kuised snapshot-failid staging-kihti.
--
-- Oluline detail:
-- kasutame siin `\copy`, mitte `COPY`.
--
-- `\copy` on psql kliendi käsk.
-- See tähendab, et failitee vaadatakse psql kliendi ehk python-konteineri seest.
-- Just sellepärast töötab siin tee `source_data/...`.
--
-- `COPY ... FROM '/tee/fail.csv'` prooviks faili lugeda andmebaasiserveri seest.
-- Selles praktikumis ei ole source_data failid andmebaasi konteineris olemas.

TRUNCATE TABLE staging.product_snapshots_raw;
TRUNCATE TABLE staging.store_snapshots_raw;

CREATE TEMP TABLE tmp_products_snapshot_import (
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    base_price_eur NUMERIC(10, 2)
);

\copy tmp_products_snapshot_import (product_id, product_name, category, base_price_eur) FROM 'source_data/products_2026_03.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO staging.product_snapshots_raw (
    snapshot_month,
    product_id,
    product_name,
    category,
    base_price_eur
)
SELECT
    DATE '2026-03-01',
    product_id,
    product_name,
    category,
    base_price_eur
FROM tmp_products_snapshot_import;

TRUNCATE TABLE tmp_products_snapshot_import;

\copy tmp_products_snapshot_import (product_id, product_name, category, base_price_eur) FROM 'source_data/products_2026_04.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO staging.product_snapshots_raw (
    snapshot_month,
    product_id,
    product_name,
    category,
    base_price_eur
)
SELECT
    DATE '2026-04-01',
    product_id,
    product_name,
    category,
    base_price_eur
FROM tmp_products_snapshot_import;

DROP TABLE tmp_products_snapshot_import;

CREATE TEMP TABLE tmp_stores_snapshot_import (
    store_id TEXT,
    store_name TEXT,
    city TEXT,
    region TEXT
);

\copy tmp_stores_snapshot_import (store_id, store_name, city, region) FROM 'source_data/stores_2026_03.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO staging.store_snapshots_raw (
    snapshot_month,
    store_id,
    store_name,
    city,
    region
)
SELECT
    DATE '2026-03-01',
    store_id,
    store_name,
    city,
    region
FROM tmp_stores_snapshot_import;

TRUNCATE TABLE tmp_stores_snapshot_import;

\copy tmp_stores_snapshot_import (store_id, store_name, city, region) FROM 'source_data/stores_2026_04.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO staging.store_snapshots_raw (
    snapshot_month,
    store_id,
    store_name,
    city,
    region
)
SELECT
    DATE '2026-04-01',
    store_id,
    store_name,
    city,
    region
FROM tmp_stores_snapshot_import;

DROP TABLE tmp_stores_snapshot_import;
