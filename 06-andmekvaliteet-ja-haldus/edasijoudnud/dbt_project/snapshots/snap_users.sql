{% snapshot snap_users %}
{{ config(
    unique_key='uuid',
    strategy='check',
    check_cols=['city', 'street', 'state', 'country'],
    target_schema='snapshots',
    dbt_valid_to_current="to_timestamp('9999-12-31', 'YYYY-MM-DD')"
) }}

SELECT
    uuid, first_name, last_name, email,
    city, street, state, country, registered_date
FROM {{ source('staging', 'users') }}
{% endsnapshot %}
