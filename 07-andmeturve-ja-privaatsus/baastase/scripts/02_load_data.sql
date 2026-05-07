\echo 'Puhastan toortabeli ja laen CSV-andmed uuesti.'

-- TRUNCATE teeb laadimise korduskäivitatavaks.
-- Kui skripti mitu korda käivitada, ei teki tabelisse duplikaate.
TRUNCATE TABLE staging.osalejad_raw;

-- \copy on psql kliendi käsk.
-- Fail loetakse client konteinerist teelt data/osalejad.csv
-- ja saadetakse andmebaasi ühenduse kaudu staging tabelisse.
\copy staging.osalejad_raw (osaleja_id, eesnimi, perenimi, email, telefon, linn, maakond, kursus, staatus, registreerumise_kuupaev) FROM 'data/osalejad.csv' WITH (FORMAT csv, HEADER true);

\echo 'Kontrollin, mitu rida laaditi.'

-- Kontrollpäring annab kiire tagasiside, kas laadimine õnnestus.
-- Oodatav tulemus selles praktikumis on 12 rida.
SELECT COUNT(*) AS laaditud_ridu
FROM staging.osalejad_raw;
