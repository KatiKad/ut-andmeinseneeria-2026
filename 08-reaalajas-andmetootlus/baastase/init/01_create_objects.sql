-- See init-skript jookseb PostgreSQL konteineri esmakordsel käivitamisel.
-- Siin loome praktikumi skeemid ja tabelid.

CREATE SCHEMA IF NOT EXISTS stream;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Sündmuste logi on praktikumi nähtav keskpunkt.
-- Iga veebipoe sündmus saab siia ühe rea.
CREATE TABLE IF NOT EXISTS stream.event_log (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_key TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    queued_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'published',
    celery_task_id TEXT,
    error_message TEXT,
    CONSTRAINT event_log_status_check
        CHECK (status IN ('published', 'queued', 'processing', 'processed', 'failed'))
);

-- Iga Celery järjekorda saatmine saab eraldi logirea.
-- Sama sündmus võib siia jõuda mitu korda, kui proovime kordustöötlust.
CREATE TABLE IF NOT EXISTS stream.task_dispatch_log (
    dispatch_id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL REFERENCES stream.event_log(event_id) ON DELETE CASCADE,
    celery_task_id TEXT NOT NULL,
    dispatch_kind TEXT NOT NULL DEFAULT 'initial',
    queued_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Korrastatud tellimuse sündmused.
-- Primaarvõti `event_id` aitab sama sündmuse topelttöötlemist vältida.
CREATE TABLE IF NOT EXISTS analytics.order_events (
    event_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    event_time TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL,
    store_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_eur NUMERIC(10, 2) NOT NULL,
    total_amount_eur NUMERIC(12, 2) NOT NULL,
    is_late BOOLEAN NOT NULL DEFAULT false
);

-- Live-koond uueneb worker'i töö käigus sündmuse kaupa.
CREATE TABLE IF NOT EXISTS analytics.sales_summary_live (
    store_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_count INTEGER NOT NULL DEFAULT 0,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    total_amount_eur NUMERIC(14, 2) NOT NULL DEFAULT 0,
    last_event_time TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (store_id, product_id)
);

-- 5 minuti aknad sündmuse aja järgi.
CREATE TABLE IF NOT EXISTS analytics.sales_windows_event_time (
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    store_id TEXT NOT NULL,
    order_count INTEGER NOT NULL,
    total_amount_eur NUMERIC(14, 2) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (window_start, store_id)
);

-- 5 minuti aknad töötluse aja järgi.
CREATE TABLE IF NOT EXISTS analytics.sales_windows_processing_time (
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    store_id TEXT NOT NULL,
    order_count INTEGER NOT NULL,
    total_amount_eur NUMERIC(14, 2) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (window_start, store_id)
);

-- Sama koond pakktöötlusena, et seda live-koondiga võrrelda.
CREATE TABLE IF NOT EXISTS analytics.sales_summary_batch (
    store_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_count INTEGER NOT NULL,
    total_quantity INTEGER NOT NULL,
    total_amount_eur NUMERIC(14, 2) NOT NULL,
    built_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (store_id, product_id)
);

-- Vigased sündmused, mida worker ei saanud analüütika tabelisse töödelda.
CREATE TABLE IF NOT EXISTS staging.bad_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,
    payload JSONB,
    error_message TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Hilinenud sündmused sündmuse aja ja töötluse aja võrdlemiseks.
CREATE TABLE IF NOT EXISTS staging.late_events (
    event_id TEXT PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL,
    delay_seconds NUMERIC(12, 2) NOT NULL,
    note TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Worker'i töötluslogi, mida on lihtsam SQL-iga lugeda kui konteineri logi.
CREATE TABLE IF NOT EXISTS monitoring.worker_task_log (
    task_log_id BIGSERIAL PRIMARY KEY,
    celery_task_id TEXT,
    event_id TEXT,
    status TEXT NOT NULL,
    message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL,
    duration_ms INTEGER
);
