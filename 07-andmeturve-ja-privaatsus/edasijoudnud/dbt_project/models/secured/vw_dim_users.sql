-- Uks vaade koik rollid jagavad. PostgreSQL pg_has_role() funktsioon kontrollib
-- iga paringu hetkel, milline roll teeb paringu, ja CASE tagastab vastava versiooni.
--
-- auditor   -> naeb toorandmeid
-- analyst   -> naeb maskeeritud PII-d
-- marketing -> naeb ainult mitte-PII tulpasid (PII tagastatakse NULL voi 'REDACTED')

{{ config(
    materialized='view',
    schema='secured',
    grants={'select': ['analyst', 'marketing', 'auditor']}
) }}

SELECT
    user_key,
    user_id,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN first_name
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_varchar('first_name') }}
        ELSE NULL
    END AS first_name,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN last_name
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_varchar('last_name') }}
        ELSE NULL
    END AS last_name,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN full_name
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_varchar('full_name') }}
        ELSE NULL
    END AS full_name,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN email
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_email('email') }}
        ELSE 'REDACTED'
    END AS email,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN city
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_varchar('city') }}
        WHEN pg_has_role(current_user, 'marketing', 'MEMBER') THEN city
        ELSE NULL
    END AS city,

    country,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN registered_date
        ELSE {{ mask_date('registered_date') }}
    END AS registered_date

FROM {{ ref('dim_users') }}
