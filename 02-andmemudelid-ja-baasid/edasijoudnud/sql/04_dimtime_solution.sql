-- ============================================================
-- 04_dimtime_solution.sql
-- Ulesanne 4 lahendus: Uus dimensioon - DimTime
-- Voimaldab tunnitaseme analyutikat
-- ============================================================

-- ============================================================
-- SAMM 1: Loo DimTime tabel
-- ============================================================

DROP TABLE IF EXISTS DimTime CASCADE;

CREATE TABLE DimTime (
    TimeKey        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Hour           INT NOT NULL CHECK (Hour BETWEEN 0 AND 23),
    MinuteBlock    VARCHAR(20),
    TimeOfDay      VARCHAR(20),
    IsBusinessHour BOOLEAN
);

-- ============================================================
-- SAMM 2: Taida 24 tunniga
-- ============================================================

INSERT INTO DimTime (Hour, MinuteBlock, TimeOfDay, IsBusinessHour)
SELECT
    h,
    '00-59',
    CASE
        WHEN h BETWEEN 6  AND 11 THEN 'Hommik'
        WHEN h BETWEEN 12 AND 13 THEN 'Lõuna'
        WHEN h BETWEEN 14 AND 17 THEN 'Pärastlõuna'
        WHEN h BETWEEN 18 AND 22 THEN 'Õhtu'
        ELSE 'Öö'
    END,
    CASE WHEN h BETWEEN 8 AND 17 THEN true ELSE false END
FROM generate_series(0, 23) AS h;

-- Kontrolli:
SELECT * FROM DimTime ORDER BY Hour;

-- ============================================================
-- SAMM 3: Lisa TimeKey veerg FactSales tabelisse
-- ============================================================

ALTER TABLE FactSales ADD COLUMN TimeKey INT REFERENCES DimTime(TimeKey);

-- Uuenda olemasolevad kirjed simuleeritud aegadega
-- (tegelikus eluolukorras tuleks see allikandmetest)
UPDATE FactSales SET TimeKey = 1 + (SaleID % 24);

-- ============================================================
-- SAMM 4: Analyutilised paringud
-- ============================================================

-- Muuk kellaaegade kaupa:
SELECT
    t.Hour,
    t.TimeOfDay,
    t.IsBusinessHour,
    COUNT(f.SaleID)    AS tehinguid,
    SUM(f.TotalAmount) AS muuk_kokku
FROM FactSales f
JOIN DimTime t ON f.TimeKey = t.TimeKey
GROUP BY t.Hour, t.TimeOfDay, t.IsBusinessHour
ORDER BY t.Hour;

-- Muuk kellaaja ja poe kaupa:
SELECT
    s.StoreName,
    t.TimeOfDay,
    SUM(f.TotalAmount) AS muuk_kokku,
    COUNT(f.SaleID)    AS tehinguid
FROM FactSales f
JOIN DimTime  t ON f.TimeKey  = t.TimeKey
JOIN DimStore s ON f.StoreKey = s.StoreKey
GROUP BY s.StoreName, t.TimeOfDay
ORDER BY s.StoreName, t.TimeOfDay;

-- Tööaeg vs mitte tööaeg:
SELECT
    CASE WHEN t.IsBusinessHour THEN 'Tööaeg (8-17)' ELSE 'Väljaspool tööaega' END AS periood,
    COUNT(f.SaleID)    AS tehinguid,
    SUM(f.TotalAmount) AS muuk_kokku,
    ROUND(100.0 * SUM(f.TotalAmount) /
        (SELECT SUM(TotalAmount) FROM FactSales), 1) AS osakaal_pct
FROM FactSales f
JOIN DimTime t ON f.TimeKey = t.TimeKey
GROUP BY t.IsBusinessHour
ORDER BY t.IsBusinessHour DESC;
