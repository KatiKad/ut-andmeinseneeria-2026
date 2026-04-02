-- ============================================================
-- 02_snowflake_solution.sql
-- Ulesanne 2 lahendus: Snowflake schema + EXPLAIN ANALYZE
-- ============================================================

-- ============================================================
-- OSA 1: Snowflake schema variant
-- ============================================================

-- Star schema: DimProduct sisaldab Category ja Brand otse veerudena
-- Snowflake: Category ja Brand on eraldi normaliseeritud tabelites
-- See vahendab andmete kordumist, aga lisab JOIN-e

-- Loome normaliseeritud tabelid
DROP TABLE IF EXISTS DimProductSnowflake CASCADE;
DROP TABLE IF EXISTS DimCategory CASCADE;
DROP TABLE IF EXISTS DimBrand CASCADE;

CREATE TABLE DimCategory (
    CategoryKey  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    CategoryName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE DimBrand (
    BrandKey  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    BrandName VARCHAR(50) NOT NULL UNIQUE
);

-- Taidame kategooriad ja braendid olemasolevast DimProduct tabelist
INSERT INTO DimCategory (CategoryName)
SELECT DISTINCT Category FROM DimProduct ORDER BY Category;

INSERT INTO DimBrand (BrandName)
SELECT DISTINCT Brand FROM DimProduct ORDER BY Brand;

-- Loome snowflake-stiilis toote tabeli
CREATE TABLE DimProductSnowflake (
    ProductKey  INT PRIMARY KEY,
    ProductName VARCHAR(100),
    CategoryKey INT REFERENCES DimCategory(CategoryKey),
    BrandKey    INT REFERENCES DimBrand(BrandKey)
);

-- Taidame snowflake toote tabeli
INSERT INTO DimProductSnowflake (ProductKey, ProductName, CategoryKey, BrandKey)
SELECT
    p.ProductKey,
    p.ProductName,
    c.CategoryKey,
    b.BrandKey
FROM DimProduct p
JOIN DimCategory c ON p.Category = c.CategoryName
JOIN DimBrand   b ON p.Brand    = b.BrandName;

-- Kontrolli:
SELECT * FROM DimProductSnowflake;
SELECT * FROM DimCategory;
SELECT * FROM DimBrand;

-- ============================================================
-- OSA 2: Vordle paringuid — Star vs Snowflake
-- ============================================================

-- Star schema paring (1 JOIN):
SELECT
    p.Category,
    SUM(f.TotalAmount) AS muuk_kokku,
    COUNT(f.SaleID) AS tehinguid
FROM FactSales f
JOIN DimProduct p ON f.ProductKey = p.ProductKey
GROUP BY p.Category
ORDER BY muuk_kokku DESC;

-- Snowflake paring (2 JOIN-i):
SELECT
    c.CategoryName,
    SUM(f.TotalAmount) AS muuk_kokku,
    COUNT(f.SaleID) AS tehinguid
FROM FactSales f
JOIN DimProductSnowflake p ON f.ProductKey = p.ProductKey
JOIN DimCategory         c ON p.CategoryKey = c.CategoryKey
GROUP BY c.CategoryName
ORDER BY muuk_kokku DESC;

-- Tulemused peaksid olema identsed!

-- ============================================================
-- OSA 3: EXPLAIN ANALYZE — joudluse vordlus
-- ============================================================

-- EXPLAIN ANALYZE naitab:
--   Planning Time:  kui kaua PostgreSQL paringu plaani koostab
--   Execution Time: kui kaua paring tegelikult jookseb
--   JOIN strateegia: Hash Join, Nested Loop, Merge Join
--   Ridade arv:     hinnanguline vs tegelik igal sammul

-- Star schema:
EXPLAIN ANALYZE
SELECT
    p.Category,
    d.DayOfWeek,
    SUM(f.TotalAmount) AS muuk_kokku,
    COUNT(f.SaleID)    AS tehinguid
FROM FactSales f
JOIN DimProduct p ON f.ProductKey = p.ProductKey
JOIN DimDate    d ON f.DateKey    = d.DateKey
GROUP BY p.Category, d.DayOfWeek
ORDER BY muuk_kokku DESC;

-- Snowflake schema:
EXPLAIN ANALYZE
SELECT
    c.CategoryName,
    d.DayOfWeek,
    SUM(f.TotalAmount) AS muuk_kokku,
    COUNT(f.SaleID)    AS tehinguid
FROM FactSales f
JOIN DimProductSnowflake p ON f.ProductKey = p.ProductKey
JOIN DimCategory         c ON p.CategoryKey = c.CategoryKey
JOIN DimDate             d ON f.DateKey     = d.DateKey
GROUP BY c.CategoryName, d.DayOfWeek
ORDER BY muuk_kokku DESC;

-- Keerukas paring koigi dimensioonidega:
EXPLAIN ANALYZE
SELECT
    d.FullDate,
    s.StoreName,
    p.ProductName,
    c.FirstName || ' ' || c.LastName AS klient,
    pm.PaymentType,
    f.Quantity,
    f.TotalAmount
FROM FactSales f
JOIN DimDate     d  ON f.DateKey     = d.DateKey
JOIN DimStore    s  ON f.StoreKey    = s.StoreKey
JOIN DimProduct  p  ON f.ProductKey  = p.ProductKey
JOIN DimCustomer c  ON f.CustomerKey = c.CustomerKey
JOIN DimPayment  pm ON f.PaymentKey  = pm.PaymentKey
ORDER BY d.FullDate, s.StoreName;

-- ============================================================
-- ARHITEKTUURIOTSUS: Star vs Snowflake
-- ============================================================
--
-- Probleem: Kuidas modelleerida toote dimensiooni?
--
-- Variandid:
--   1. Star schema: Category ja Brand otse DimProduct tabelis
--   2. Snowflake: Category ja Brand eraldi normaliseeritud tabelites
--
-- Valik ja pohjendus:
--   Star schema on eelistatud andmeladudes, sest:
--   - Vahem JOIN-e = lihtsam ja kiirem
--   - Arikasjatajad moistavad paremini
--   - Moodne riistvara muudab liigse salvestusruumi probleemi
--     tahtsusetuks
--
-- Kompromissid:
--   - Andmete korduvus (Category kordub igas DimProduct reas)
--   - Dimensiooni uuendamine nouab rohkem ridu
--   - Snowflake voimaldab rangemat referentsiaalset terviklikkust
--
-- Kokkuvote:
--   Star schema eelised:
--     + Lihtsam paringud (vahem JOIN-e)
--     + Tavaliselt kiirem (vahem tabelite uhendamist)
--     + Paremini mooistetav arikasjatajatele
--
--   Snowflake schema eelised:
--     + Vahem andmete kordumist (normaliseeritud)
--     + Lihtsam dimensioonide uuendamine
--     + Vahem salvestusruumi (suurte andmemahtude korral)
--
--   Praktikas: Star schema on enamasti eelistatud,
--   sest paringu kiirus on olulisem kui salvestusruum.
