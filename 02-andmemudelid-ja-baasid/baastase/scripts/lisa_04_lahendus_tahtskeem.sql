-- Lisaülesande üks võimalik lahendus rikkama veebipoe andmestiku jaoks.
--
-- Skript eeldab, et käivitad selle `psql` sees.
--
-- Lahendus teeb neli asja:
-- 1. loob ja täidab laia lähtetabeli source_muuk_laiem
-- 2. loob kuupäeva-, kliendi-, toote-, kampaania- ja makseviisi dimensioonid
-- 3. loob faktitabeli fact_muuk_lisa
-- 4. käivitab lõpus kaks kontrollpäringut

-- ---------------------------------------------------------------------
-- 1. Korista eelmine lisaülesande lahendus ära
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS fact_muuk_lisa;
DROP TABLE IF EXISTS dim_makseviis_lisa;
DROP TABLE IF EXISTS dim_kampaania_lisa;
DROP TABLE IF EXISTS dim_toode_lisa;
DROP TABLE IF EXISTS dim_klient_lisa;
DROP TABLE IF EXISTS dim_kuupaev_lisa;
DROP TABLE IF EXISTS source_muuk_laiem;

-- ---------------------------------------------------------------------
-- 2. Lähtetabel ja toorandmete laadimine
-- ---------------------------------------------------------------------

CREATE TABLE source_muuk_laiem (
    tellimuse_nr INTEGER NOT NULL,
    kuupaev DATE NOT NULL,
    kliendi_id INTEGER NOT NULL,
    kliendi_nimi TEXT NOT NULL,
    kliendi_linn TEXT NOT NULL,
    kliendityyp TEXT NOT NULL,
    toote_nimi TEXT NOT NULL,
    kategooria TEXT NOT NULL,
    tootemark TEXT NOT NULL,
    kampaania_nimi TEXT NOT NULL,
    kampaania_tyyp TEXT NOT NULL,
    liiklusallikas TEXT NOT NULL,
    makseviis TEXT NOT NULL,
    kogus INTEGER NOT NULL,
    uhikuhind NUMERIC(10,2) NOT NULL,
    muugisumma NUMERIC(10,2) NOT NULL
);

COPY source_muuk_laiem (
    tellimuse_nr,
    kuupaev,
    kliendi_id,
    kliendi_nimi,
    kliendi_linn,
    kliendityyp,
    toote_nimi,
    kategooria,
    tootemark,
    kampaania_nimi,
    kampaania_tyyp,
    liiklusallikas,
    makseviis,
    kogus,
    uhikuhind,
    muugisumma
)
FROM '/data/veebipoe_muuk_lisaulesanne.csv'
WITH (FORMAT csv, HEADER true);

-- ---------------------------------------------------------------------
-- 3. Dimensioonid
-- ---------------------------------------------------------------------

-- Kuupäeva dimensiooni loome otse toorandmestiku minimaalse ja maksimaalse
-- kuupäeva vahemikust. Nii ei pea kuupäevi failis käsitsi ette kirjutama.
CREATE TABLE dim_kuupaev_lisa AS
WITH piirid AS (
    SELECT
        MIN(kuupaev) AS algus_kuupaev,
        MAX(kuupaev) AS lopp_kuupaev
    FROM source_muuk_laiem
),
kuupaevad AS (
    SELECT generate_series(algus_kuupaev, lopp_kuupaev, INTERVAL '1 day')::DATE AS kuupaev
    FROM piirid
)
SELECT
    TO_CHAR(kuupaev, 'YYYYMMDD')::INTEGER AS kuupaev_key,
    kuupaev,
    EXTRACT(DAY FROM kuupaev)::INTEGER AS paeva_nr_kuus,
    EXTRACT(DOY FROM kuupaev)::INTEGER AS paeva_nr_aastas,
    EXTRACT(ISODOW FROM kuupaev)::INTEGER AS nadalapaev_nr,
    CASE EXTRACT(ISODOW FROM kuupaev)::INTEGER
        WHEN 1 THEN 'esmaspaev'
        WHEN 2 THEN 'teisipaev'
        WHEN 3 THEN 'kolmapaev'
        WHEN 4 THEN 'neljapaev'
        WHEN 5 THEN 'reede'
        WHEN 6 THEN 'laupaev'
        WHEN 7 THEN 'puhapaev'
    END AS nadalapaev_nimi,
    EXTRACT(WEEK FROM kuupaev)::INTEGER AS nadal_nr,
    EXTRACT(MONTH FROM kuupaev)::INTEGER AS kuu_nr,
    CASE EXTRACT(MONTH FROM kuupaev)::INTEGER
        WHEN 1 THEN 'jaanuar'
        WHEN 2 THEN 'veebruar'
        WHEN 3 THEN 'marts'
        WHEN 4 THEN 'aprill'
        WHEN 5 THEN 'mai'
        WHEN 6 THEN 'juuni'
        WHEN 7 THEN 'juuli'
        WHEN 8 THEN 'august'
        WHEN 9 THEN 'september'
        WHEN 10 THEN 'oktoober'
        WHEN 11 THEN 'november'
        WHEN 12 THEN 'detsember'
    END AS kuu_nimi,
    EXTRACT(QUARTER FROM kuupaev)::INTEGER AS kvartal,
    EXTRACT(YEAR FROM kuupaev)::INTEGER AS aasta,
    CASE
        WHEN EXTRACT(ISODOW FROM kuupaev)::INTEGER IN (6, 7) THEN 1
        ELSE 0
    END AS nadalavahetus_ind,
    CASE
        WHEN EXTRACT(ISODOW FROM kuupaev)::INTEGER BETWEEN 1 AND 5 THEN 1
        ELSE 0
    END AS toopaev_ind
FROM kuupaevad
ORDER BY kuupaev;

ALTER TABLE dim_kuupaev_lisa
ADD PRIMARY KEY (kuupaev_key);

CREATE TABLE dim_klient_lisa (
    klient_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kliendi_id INTEGER NOT NULL UNIQUE,
    kliendi_nimi TEXT NOT NULL,
    kliendi_linn TEXT NOT NULL,
    kliendityyp TEXT NOT NULL
);

INSERT INTO dim_klient_lisa (kliendi_id, kliendi_nimi, kliendi_linn, kliendityyp)
SELECT DISTINCT
    kliendi_id,
    kliendi_nimi,
    kliendi_linn,
    kliendityyp
FROM source_muuk_laiem
ORDER BY kliendi_id;

-- Toote dimensioonis kasutame loomuliku unikaalsusena toote nime ja
-- tootemärgi kombinatsiooni. Toorandmestikus eraldi tootekoodi ei ole.
--
-- Selle lahenduse piirang on, et see mudel ei toeta aeglaselt muutuvat
-- dimensiooni toote kategooria jaoks. Kui sama toote kategooria muutuks,
-- kirjutaks see mudel sisuliselt vana ja uue seisundi üheks kirjeks kokku
-- ning ainult uue rea lisamisest ei piisaks.
--
-- Selle võimaldamiseks oleks vaja andmeallikast lisainfot, näiteks
-- kategooria kehtivuse alguse või versiooni kohta, et saaksime hoida
-- sama toote kohta ajaloos mitu eri dimensioonirida.
CREATE TABLE dim_toode_lisa (
    toode_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    toote_nimi TEXT NOT NULL,
    kategooria TEXT NOT NULL,
    tootemark TEXT NOT NULL,
    UNIQUE (toote_nimi, tootemark)
);

INSERT INTO dim_toode_lisa (toote_nimi, kategooria, tootemark)
SELECT DISTINCT
    toote_nimi,
    kategooria,
    tootemark
FROM source_muuk_laiem
ORDER BY toote_nimi, tootemark;

CREATE TABLE dim_kampaania_lisa (
    kampaania_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kampaania_nimi TEXT NOT NULL,
    kampaania_tyyp TEXT NOT NULL,
    liiklusallikas TEXT NOT NULL,
    UNIQUE (kampaania_nimi, kampaania_tyyp, liiklusallikas)
);

INSERT INTO dim_kampaania_lisa (kampaania_nimi, kampaania_tyyp, liiklusallikas)
SELECT DISTINCT
    kampaania_nimi,
    kampaania_tyyp,
    liiklusallikas
FROM source_muuk_laiem
ORDER BY kampaania_nimi, kampaania_tyyp, liiklusallikas;

CREATE TABLE dim_makseviis_lisa (
    makseviis_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    makseviis TEXT NOT NULL UNIQUE
);

INSERT INTO dim_makseviis_lisa (makseviis)
SELECT DISTINCT
    makseviis
FROM source_muuk_laiem
ORDER BY makseviis;

-- ---------------------------------------------------------------------
-- 4. Faktitabel
-- ---------------------------------------------------------------------

-- Selles lahenduses ei salvesta me ühikuhinda faktitabelisse.
-- Põhimõõdikud on kogus ja müügisumma, sest need vastavad paremini
-- granulaarsuse lausele ja neid on loomulik kokku liita.
CREATE TABLE fact_muuk_lisa (
    muuk_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kuupaev_key INTEGER NOT NULL REFERENCES dim_kuupaev_lisa (kuupaev_key),
    tellimuse_nr INTEGER NOT NULL,
    klient_key INTEGER NOT NULL REFERENCES dim_klient_lisa (klient_key),
    toode_key INTEGER NOT NULL REFERENCES dim_toode_lisa (toode_key),
    kampaania_key INTEGER NOT NULL REFERENCES dim_kampaania_lisa (kampaania_key),
    makseviis_key INTEGER NOT NULL REFERENCES dim_makseviis_lisa (makseviis_key),
    kogus INTEGER NOT NULL,
    muugisumma NUMERIC(10,2) NOT NULL
);

INSERT INTO fact_muuk_lisa (
    kuupaev_key,
    tellimuse_nr,
    klient_key,
    toode_key,
    kampaania_key,
    makseviis_key,
    kogus,
    muugisumma
)
SELECT
    TO_CHAR(s.kuupaev, 'YYYYMMDD')::INTEGER AS kuupaev_key,
    s.tellimuse_nr,
    k.klient_key,
    t.toode_key,
    kp.kampaania_key,
    m.makseviis_key,
    s.kogus,
    s.muugisumma
FROM source_muuk_laiem s
JOIN dim_klient_lisa k
    ON s.kliendi_id = k.kliendi_id
JOIN dim_toode_lisa t
    ON s.toote_nimi = t.toote_nimi
   AND s.tootemark = t.tootemark
JOIN dim_kampaania_lisa kp
    ON s.kampaania_nimi = kp.kampaania_nimi
   AND s.kampaania_tyyp = kp.kampaania_tyyp
   AND s.liiklusallikas = kp.liiklusallikas
JOIN dim_makseviis_lisa m
    ON s.makseviis = m.makseviis
ORDER BY s.kuupaev, s.tellimuse_nr, s.toote_nimi;

-- ---------------------------------------------------------------------
-- 5. Kiired kontrollid
-- ---------------------------------------------------------------------

-- Ridade arvud. Need aitavad kiiresti kontrollida, et kõik laadimised on toimunud.
SELECT 'source_muuk_laiem' AS tabel, COUNT(*) AS ridu FROM source_muuk_laiem
UNION ALL
SELECT 'dim_kuupaev_lisa', COUNT(*) FROM dim_kuupaev_lisa
UNION ALL
SELECT 'dim_klient_lisa', COUNT(*) FROM dim_klient_lisa
UNION ALL
SELECT 'dim_toode_lisa', COUNT(*) FROM dim_toode_lisa
UNION ALL
SELECT 'dim_kampaania_lisa', COUNT(*) FROM dim_kampaania_lisa
UNION ALL
SELECT 'dim_makseviis_lisa', COUNT(*) FROM dim_makseviis_lisa
UNION ALL
SELECT 'fact_muuk_lisa', COUNT(*) FROM fact_muuk_lisa
ORDER BY tabel;

-- Kontrollpäring 1.
-- Kas kuupäeva- ja kampaaniadimensioonid töötavad nii, et saame
-- vaadata müüki nädalapäeva ja kampaaniatüübi lõikes?
SELECT
    d.nadalapaev_nimi,
    kp.kampaania_tyyp,
    SUM(f.muugisumma) AS muuk_kokku
FROM fact_muuk_lisa f
JOIN dim_kuupaev_lisa d
    ON f.kuupaev_key = d.kuupaev_key
JOIN dim_kampaania_lisa kp
    ON f.kampaania_key = kp.kampaania_key
GROUP BY
    d.nadalapaev_nimi,
    kp.kampaania_tyyp
ORDER BY
    kp.kampaania_tyyp,
    d.nadalapaev_nimi;

-- Kontrollpäring 2.
-- Kas kliendi- ja tootedimensioonid lubavad vaadata müüki
-- klienditüübi ja kategooria kaupa?
SELECT
    k.kliendityyp,
    t.kategooria,
    SUM(f.muugisumma) AS muuk_kokku
FROM fact_muuk_lisa f
JOIN dim_klient_lisa k
    ON f.klient_key = k.klient_key
JOIN dim_toode_lisa t
    ON f.toode_key = t.toode_key
GROUP BY
    k.kliendityyp,
    t.kategooria
ORDER BY
    k.kliendityyp,
    muuk_kokku DESC,
    t.kategooria;
