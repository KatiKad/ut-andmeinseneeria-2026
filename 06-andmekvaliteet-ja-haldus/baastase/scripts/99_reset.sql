DROP TABLE IF EXISTS analytics.daily_product_sales_clean;
DROP TABLE IF EXISTS analytics.quality_overview;
DROP TABLE IF EXISTS quality.orders_clean;
DROP TABLE IF EXISTS quality.order_issue_summary;
DROP TABLE IF EXISTS quality.order_rule_results;
DROP TABLE IF EXISTS intermediate.dim_products_scd;
DROP TABLE IF EXISTS intermediate.dim_stores_scd;

TRUNCATE TABLE
    staging.orders_raw,
    staging.product_snapshots_raw,
    staging.store_snapshots_raw,
    governance.data_asset_registry
RESTART IDENTITY;
