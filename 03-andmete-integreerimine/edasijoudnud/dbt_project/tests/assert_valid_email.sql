-- Kohandatud test: kontrollib, et koigil kasutajatel on kehtiv meiliaadress.
-- Test laebib, kui paring tagastab 0 rida (st koik meiliaadressid sisaldavad @).
-- Kui see paring tagastab ridu, tahendab see, et andmetes on vigaseid meiliaadrsse.

SELECT *
FROM {{ ref('int_users') }}
WHERE email NOT LIKE '%@%'
