-- Intermediate: kasutajate puhastamine ja normaliseerimine
-- staging (pronks) -> intermediate (hobe)

SELECT
    id          AS user_id,
    uuid,
    INITCAP(TRIM(first_name))   AS first_name,
    INITCAP(TRIM(last_name))    AS last_name,
    LOWER(TRIM(email))          AS email,
    TRIM(city)                  AS city,
    TRIM(state)                 AS state,
    TRIM(country)               AS country,
    TRIM(street)                AS street,
    TRIM(postcode)              AS postcode,
    registered_date,
    loaded_at
FROM {{ source('staging', 'users') }}
WHERE uuid IS NOT NULL
