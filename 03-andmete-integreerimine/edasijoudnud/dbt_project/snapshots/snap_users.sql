-- SCD Type 2 snapshot kasutajate aadressimuudatuste jalgimiseks.
--
-- Strateegia: check — dbt vordleb check_cols veerge.
-- Kui city, street, state voi country on muutunud, loob dbt uue versiooni:
--   vana rida saab dbt_valid_to vaartuse (pole enam kehtiv)
--   uus rida saab dbt_valid_to = 9999-12-31 (kehtiv versioon)

{% snapshot snap_users %}

{{ config(
    unique_key='uuid',
    strategy='check',
    check_cols=['city', 'street', 'state', 'country'],
    target_schema='snapshots',
    dbt_valid_to_current="to_timestamp('9999-12-31', 'YYYY-MM-DD')"
) }}

SELECT
    uuid,
    first_name,
    last_name,
    email,
    city,
    street,
    state,
    country,
    registered_date
FROM {{ source('staging', 'users') }}

{% endsnapshot %}
