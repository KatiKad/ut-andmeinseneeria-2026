-- Postituste vaade kõigi rollide jaoks - sisu nähtavus sõltub rollist.
--
-- auditor   -> naeb postituste sisu ja autori nime
-- analyst   -> naeb sisu, autori nimi maskeeritud
-- marketing -> naeb ainult statistikat (post_id, body_length); sisu ja autor NULL

{{ config(
    materialized='view',
    schema='secured',
    grants={'select': ['analyst', 'marketing', 'auditor']}
) }}

SELECT
    post_id,
    user_key,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN author_name
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_varchar('author_name') }}
        ELSE NULL
    END AS author_name,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER')
          OR pg_has_role(current_user, 'analyst', 'MEMBER') THEN title
        ELSE NULL
    END AS title,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER')
          OR pg_has_role(current_user, 'analyst', 'MEMBER') THEN body
        ELSE NULL
    END AS body,

    body_length,
    loaded_at

FROM {{ ref('fct_posts') }}
