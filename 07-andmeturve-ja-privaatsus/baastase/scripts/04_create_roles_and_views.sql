\echo 'Loon rollid analyytik, aruandlus ja auditor, kui neid veel ei ole.'

-- Rollid kirjeldavad tööülesandeid, mitte konkreetseid inimesi.
-- NOLOGIN tähendab, et rolliga ei saa otse sisse logida.
-- Praktikumis kasutatakse rolle SET ROLE käsuga, et näha õiguste erinevust.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analyytik') THEN
        CREATE ROLE analyytik NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aruandlus') THEN
        CREATE ROLE aruandlus NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auditor') THEN
        CREATE ROLE auditor NOLOGIN;
    END IF;
END
$$;

\echo 'Loon maskeeritud analyytiku vaate.'

-- Analyytik vajab reataseme andmeid, kuid mitte täisnime ega täiskontakti.
-- Rida jääb alles, kuid otsese PII väljad maskeeritakse.
CREATE OR REPLACE VIEW secured.v_osalejad_analyytik AS
SELECT
    osaleja_id,
    -- Nimeväljadest jääb nähtavaks ainult esimene täht.
    left(eesnimi, 1) || repeat('*', greatest(char_length(eesnimi) - 1, 0)) AS eesnimi_maskitud,
    left(perenimi, 1) || repeat('*', greatest(char_length(perenimi) - 1, 0)) AS perenimi_maskitud,
    -- E-posti puhul jääb alles esimene täht ja domeen.
    CASE
        WHEN position('@' IN email) > 1
            THEN left(email, 1) || '***@' || split_part(email, '@', 2)
        ELSE '***'
    END AS email_maskitud,
    -- Telefoninumbrist jäävad alles ainult algus ja lõpp.
    left(telefon, 4) || ' *** ' || right(telefon, 2) AS telefon_maskitud,
    linn,
    maakond,
    kursus,
    staatus,
    registreerumise_kuupaev
FROM staging.osalejad_raw;

COMMENT ON VIEW secured.v_osalejad_analyytik IS
    'Analyytiku vaade. Nimi, e-post ja telefon on maskeeritud.';

\echo 'Loon aruandluse koondvaate.'

-- Aruandlus ei vaja üksikute inimeste ridu.
-- Koondvaates on ainult rühmad ja arvud, mitte nimed ega kontaktandmed.
CREATE OR REPLACE VIEW secured.v_osalejad_aruandlus AS
SELECT
    kursus,
    maakond,
    staatus,
    COUNT(*)::INTEGER AS osalejate_arv,
    MIN(registreerumise_kuupaev) AS esimene_registreerumine,
    MAX(registreerumise_kuupaev) AS viimane_registreerumine
FROM staging.osalejad_raw
GROUP BY kursus, maakond, staatus;

COMMENT ON VIEW secured.v_osalejad_aruandlus IS
    'Aruandluse koondvaade. Reataseme isikuandmeid ei ole.';

\echo 'Eemaldan vaikimisi avalikud õigused ja annan rollidele ainult vajaliku.'

-- Kõigepealt eemaldatakse vaikimisi ligipääs.
-- PUBLIC tähendab kõiki rolle. Tundlike andmete puhul ei ole see sobiv vaikimisi ligipääs.
REVOKE ALL ON SCHEMA staging FROM PUBLIC;
REVOKE ALL ON SCHEMA governance FROM PUBLIC;
REVOKE ALL ON SCHEMA secured FROM PUBLIC;

-- Sama põhimõte tabelite ja vaadete kohta.
REVOKE ALL ON ALL TABLES IN SCHEMA staging FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA governance FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA secured FROM PUBLIC;

-- Kui skripti käivitatakse uuesti, lähtestatakse rollide õigused.
REVOKE ALL ON SCHEMA staging FROM analyytik, aruandlus, auditor;
REVOKE ALL ON SCHEMA governance FROM analyytik, aruandlus, auditor;
REVOKE ALL ON SCHEMA secured FROM analyytik, aruandlus, auditor;

REVOKE ALL ON ALL TABLES IN SCHEMA staging FROM analyytik, aruandlus, auditor;
REVOKE ALL ON ALL TABLES IN SCHEMA governance FROM analyytik, aruandlus, auditor;
REVOKE ALL ON ALL TABLES IN SCHEMA secured FROM analyytik, aruandlus, auditor;

-- PII registrit tohivad kõik kolm rolli lugeda.
-- Registris ei ole toorandmeid, vaid kirjeldus selle kohta, kuidas veerge käsitleda.
GRANT USAGE ON SCHEMA governance TO analyytik, aruandlus, auditor;
GRANT SELECT ON governance.pii_register TO analyytik, aruandlus, auditor;

-- Tavakasutuse rollid saavad lugeda ainult neile mõeldud secured vaateid.
-- Auditor saab lugeda mõlemat vaadet, et kontrollida jagatavat andmekuju.
GRANT USAGE ON SCHEMA secured TO analyytik, aruandlus, auditor;
GRANT SELECT ON secured.v_osalejad_analyytik TO analyytik, auditor;
GRANT SELECT ON secured.v_osalejad_aruandlus TO aruandlus, auditor;

-- Auditor on erandlik kontrolliroll.
-- Tema näeb nii toortabelit kui ka turvatud vaateid,
-- et saaks võrrelda algset, maskeeritud ja koondatud kuju.
GRANT USAGE ON SCHEMA staging TO auditor;
GRANT SELECT ON staging.osalejad_raw TO auditor;

\echo 'Rollid, vaated ja õigused on valmis.'
