-- Kasutajate dimensioonitabel
-- intermediate (hõbe) -> marts (kuld)

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
