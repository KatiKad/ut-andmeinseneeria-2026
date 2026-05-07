{{ config(
    materialized='incremental',
    unique_key='user_key'
) }}

SELECT
    u.uuid              AS user_key,
    u.first_name,
    u.last_name,
    COUNT(p.post_id)    AS total_posts,
    AVG(LENGTH(p.body)) AS avg_post_length,
    MAX(p.loaded_at)    AS last_post_loaded_at
FROM {{ ref('int_users') }} u
LEFT JOIN {{ ref('int_posts') }} p
    ON u.user_id = p.user_id
{% if is_incremental() %}
WHERE p.loaded_at > (SELECT MAX(last_post_loaded_at) FROM {{ this }})
{% endif %}
GROUP BY u.uuid, u.first_name, u.last_name
