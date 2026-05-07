SELECT *
FROM {{ ref('int_users') }}
WHERE email NOT LIKE '%@%'
