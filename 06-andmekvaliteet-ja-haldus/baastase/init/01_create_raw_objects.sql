CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS quality;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS governance;

CREATE TABLE IF NOT EXISTS staging.product_snapshots_raw (
    snapshot_month DATE NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    base_price_eur NUMERIC(10, 2) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (snapshot_month, product_id)
);

CREATE TABLE IF NOT EXISTS staging.store_snapshots_raw (
    snapshot_month DATE NOT NULL,
    store_id TEXT NOT NULL,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (snapshot_month, store_id)
);

CREATE TABLE IF NOT EXISTS staging.orders_raw (
    staging_row_id BIGSERIAL PRIMARY KEY,
    order_id TEXT,
    order_date DATE NOT NULL,
    store_id TEXT,
    product_id TEXT,
    quantity INTEGER,
    unit_price_eur NUMERIC(10, 2),
    source_updated_at TIMESTAMPTZ NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_raw_order_date
    ON staging.orders_raw (order_date);

CREATE TABLE IF NOT EXISTS governance.data_asset_registry (
    asset_name TEXT PRIMARY KEY,
    asset_layer TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    steward_name TEXT NOT NULL,
    refresh_frequency TEXT NOT NULL,
    source_system TEXT NOT NULL,
    business_description TEXT NOT NULL,
    contains_personal_data BOOLEAN NOT NULL DEFAULT FALSE,
    quality_notes TEXT,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
