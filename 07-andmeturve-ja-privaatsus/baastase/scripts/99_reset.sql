\echo 'Eemaldan praktikumi skeemid ja rollid.'

-- Reset-skript on mõeldud puhtaks uueks alguseks.
-- CASCADE eemaldab koos skeemidega ka nende sees olevad tabelid ja vaated.
DROP SCHEMA IF EXISTS secured CASCADE;
DROP SCHEMA IF EXISTS governance CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;

-- Rollid tuleb eemaldada pärast skeeme, sest objektidel võivad olla rollidele antud õigused.
DROP ROLE IF EXISTS juhendaja;
DROP ROLE IF EXISTS analyytik;
DROP ROLE IF EXISTS aruandlus;
DROP ROLE IF EXISTS auditor;

\echo 'Praktikumi andmebaasi objektid on eemaldatud.'
