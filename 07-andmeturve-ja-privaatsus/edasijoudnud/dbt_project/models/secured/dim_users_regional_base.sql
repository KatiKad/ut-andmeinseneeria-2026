-- Regiooni juhi vaade: kaks turbemehhanismi korraga
--
-- 1. Row-Level Security (post_hook): regional_manager näeb ainult omaregiooni kasutajaid
--    SET app.current_region = 'Estonia'; -> näed ainult Eesti kasutajaid
--    SET app.current_region = 'Finland'; -> näed ainult Soome kasutajaid
--
-- 2. Column-Level Security (post_hook): email veerg on tabelis olemas, aga ilma GRANT-ita
--    SELECT email FROM secured.dim_users_regional_base -> ERROR: permission denied for column "email"
--    SELECT first_name, city, country FROM ...          -> toimib (need veerud on GRANT-is)
--    Stsenaarium B: veerg on olemas aga keelatud
--
-- auditor pääseb ligi täielikult (GRANT SELECT ON ... TO auditor)

{{ config(
    materialized='table',
    schema='secured',
    post_hook=[
        "GRANT SELECT ON {{ this }} TO auditor",
        "{{ enable_rls_by_region(this, region_col='country') }}",
        "{{ grant_column_level(this, role='regional_manager', columns=['user_key', 'user_id', 'first_name', 'last_name', 'full_name', 'city', 'country', 'registered_date']) }}"
    ]
) }}

SELECT
    user_key,
    user_id,
    first_name,
    last_name,
    full_name,
    email,
    city,
    country,
    registered_date
FROM {{ ref('dim_users') }}
