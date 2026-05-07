-- Kasutajate dimensioonitabel
-- intermediate (hobe) -> marts (kuld)
-- Auditor-roll paaseb siia otse (grants konfiguratsioonis)

SELECT
    uuid                                    AS user_key,
    user_id,
    first_name,
    last_name,
    first_name || ' ' || last_name          AS full_name,
    email,
    city,
    country,
    registered_date
FROM {{ ref('int_users') }}
