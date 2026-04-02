-- Tabelite eemaldamine (õiges järjekorras, et FK-d ei segaks)
DROP TABLE IF EXISTS fact_muuk;
DROP TABLE IF EXISTS dim_toode;
DROP TABLE IF EXISTS dim_klient;
DROP TABLE IF EXISTS dim_kuupaev;

-- Kuupäeva dimensioon
CREATE TABLE dim_kuupaev AS
WITH piirid AS (
    SELECT
        MIN(kuupaev) AS algus_kuupaev,
        MAX(kuupaev) AS lopp_kuupaev
    FROM source_muuk
),
kuupaevad AS (
    SELECT generate_series(algus_kuupaev, lopp_kuupaev, INTERVAL '1 day')::DATE AS kuupaev
    FROM piirid
)
SELECT
    TO_CHAR(kuupaev, 'YYYYMMDD')::INTEGER AS kuupaev_key,
    kuupaev,
    EXTRACT(DAY FROM kuupaev)::INTEGER AS paeva_nr_kuus,
    EXTRACT(ISODOW FROM kuupaev)::INTEGER AS nadalapaev_nr,
    EXTRACT(WEEK FROM kuupaev)::INTEGER AS nadal_nr,
    EXTRACT(MONTH FROM kuupaev)::INTEGER AS kuu_nr,
    EXTRACT(QUARTER FROM kuupaev)::INTEGER AS kvartal,
    EXTRACT(YEAR FROM kuupaev)::INTEGER AS aasta
FROM kuupaevad
ORDER BY kuupaev;

ALTER TABLE dim_kuupaev ADD PRIMARY KEY (kuupaev_key);

-- Kliendi dimensioon
CREATE TABLE dim_klient (
    klient_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kliendi_id TEXT NOT NULL UNIQUE,
    kliendi_nimi TEXT NOT NULL,
    kliendityyp TEXT NOT NULL
);

-- Toote dimensioon
CREATE TABLE dim_toode (
    toode_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    toote_kood TEXT NOT NULL UNIQUE,
    toote_nimi TEXT NOT NULL,
    kategooria TEXT NOT NULL
);

-- Faktitabel – viitab kuupaev_key kaudu dim_kuupaev tabelile
CREATE TABLE fact_muuk (
    muuk_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kuupaev_key INTEGER NOT NULL REFERENCES dim_kuupaev (kuupaev_key),
    tellimuse_nr TEXT NOT NULL,
    klient_key INTEGER NOT NULL REFERENCES dim_klient (klient_key),
    toode_key INTEGER NOT NULL REFERENCES dim_toode (toode_key),
    kogus INTEGER NOT NULL,
    muugisumma NUMERIC(10,2) NOT NULL
);

-- Andmete laadimine
TRUNCATE TABLE fact_muuk, dim_toode, dim_klient RESTART IDENTITY;

INSERT INTO dim_klient (kliendi_id, kliendi_nimi, kliendityyp)
SELECT DISTINCT kliendi_id, kliendi_nimi, kliendityyp
FROM source_muuk
ORDER BY kliendi_id;

INSERT INTO dim_toode (toote_kood, toote_nimi, kategooria)
SELECT DISTINCT toote_kood, toote_nimi, kategooria
FROM source_muuk
ORDER BY toote_kood;

INSERT INTO fact_muuk (
    kuupaev_key,
    tellimuse_nr,
    klient_key,
    toode_key,
    kogus,
    muugisumma
)
SELECT
    TO_CHAR(s.kuupaev, 'YYYYMMDD')::INTEGER AS kuupaev_key,
    s.tellimuse_nr,
    k.klient_key,
    t.toode_key,
    s.kogus,
    ROUND((s.kogus * s.uhikuhind)::NUMERIC, 2) AS muugisumma
FROM source_muuk s
JOIN dim_klient k ON s.kliendi_id = k.kliendi_id
JOIN dim_toode t ON s.toote_kood = t.toote_kood
ORDER BY s.kuupaev, s.tellimuse_nr, s.toote_kood;
