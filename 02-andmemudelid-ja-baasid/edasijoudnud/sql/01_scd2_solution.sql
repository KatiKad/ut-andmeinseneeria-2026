-- ============================================================
-- 01_scd2_solution.sql
-- Ulesanne 1 lahendus: SCD Type 2 implementeerimine
-- Stsenaarium: Alice Smith kolib Tallinnast Tartusse
-- ============================================================

-- Kontrolli praegust seisu:
SELECT * FROM DimCustomer ORDER BY CustomerKey;

-- ============================================================
-- SAMM 1: Lisa SCD2 valjad DimCustomer tabelisse
-- ============================================================

ALTER TABLE DimCustomer ADD COLUMN ValidFrom DATE;
ALTER TABLE DimCustomer ADD COLUMN ValidTo DATE;

-- ============================================================
-- SAMM 2: Sea olemasolevate kirjete vaikimisi vaartused
-- ============================================================

UPDATE DimCustomer
SET ValidFrom = '2025-01-01',
    ValidTo   = '9999-12-31';

-- Kontrolli vahetulemust:
SELECT * FROM DimCustomer ORDER BY CustomerKey;

-- ============================================================
-- SAMM 3: Sulge Alice'i vana kirje
-- ============================================================

UPDATE DimCustomer
SET ValidTo = CURRENT_DATE - INTERVAL '1 day'
WHERE CustomerID = 1
  AND ValidTo = '9999-12-31';

-- ============================================================
-- SAMM 4: Lisa uus kirje Alice'ile uue aadressiga (Tartu)
-- ============================================================

INSERT INTO DimCustomer (CustomerID, FirstName, LastName, Segment, City, ValidFrom, ValidTo)
VALUES (
    1,              -- sama CustomerID (ariline ID)
    'Alice',
    'Smith',
    'Regular',
    'Tartu',        -- uus linn
    CURRENT_DATE,
    '9999-12-31'
);

-- ============================================================
-- SAMM 5: Kontrolli tulemust
-- ============================================================

-- Koik kliendid:
SELECT * FROM DimCustomer ORDER BY CustomerID, ValidFrom;

-- Alice'i ajalugu:
SELECT
    CustomerKey,
    CustomerID,
    FirstName || ' ' || LastName AS nimi,
    City,
    ValidFrom,
    ValidTo,
    CASE WHEN ValidTo = '9999-12-31' THEN 'Aktiivne' ELSE 'Ajalugu' END AS staatus
FROM DimCustomer
WHERE CustomerID = 1
ORDER BY ValidFrom;

-- ============================================================
-- SAMM 6: Lisa muugitehing Alice'i uuele kirjele
-- ============================================================

-- Leia Alice'i uus CustomerKey
-- (viimane lisatud kirje Tartu aadressiga)
INSERT INTO FactSales (DateKey, StoreKey, ProductKey, CustomerKey, PaymentKey, Quantity, UnitPrice, TotalAmount)
SELECT
    d.DateKey,
    s.StoreKey,
    p.ProductKey,
    c.CustomerKey,
    pm.PaymentKey,
    3,          -- kogus
    1.20,       -- uhikuhind
    3.60        -- kogusumma
FROM DimDate d, DimStore s, DimProduct p, DimCustomer c, DimPayment pm
WHERE d.FullDate = (SELECT CURRENT_DATE)
  AND s.City = 'Tartu'
  AND p.ProductName = 'Õun'
  AND c.CustomerID = 1 AND c.ValidTo = '9999-12-31'
  AND pm.PaymentType = 'Kaart'
LIMIT 1;

-- ============================================================
-- SAMM 7: Muuk linnade kaupa (labi ajaloo)
-- ============================================================

-- Alice'i muugid labi kogu ajaloo (koik versioonid):
SELECT
    c.City,
    c.ValidFrom,
    c.ValidTo,
    CASE WHEN c.ValidTo = '9999-12-31' THEN 'Aktiivne' ELSE 'Ajalugu' END AS staatus,
    COUNT(f.SaleID) AS tehinguid,
    COALESCE(SUM(f.TotalAmount), 0) AS muuk_kokku
FROM DimCustomer c
LEFT JOIN FactSales f ON c.CustomerKey = f.CustomerKey
WHERE c.CustomerID = 1
GROUP BY c.City, c.ValidFrom, c.ValidTo
ORDER BY c.ValidFrom;

-- Ainult aktiivne versioon:
SELECT
    c.FirstName || ' ' || c.LastName AS nimi,
    c.City,
    SUM(f.TotalAmount) AS muuk_kokku
FROM FactSales f
JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey
WHERE c.CustomerID = 1
  AND c.ValidTo = '9999-12-31'
GROUP BY c.FirstName, c.LastName, c.City;
