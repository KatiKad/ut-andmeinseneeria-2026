-- Intermediate: postituste puhastamine
-- staging (pronks) -> intermediate (hobe)

SELECT
    id          AS post_id,
    user_id,
    TRIM(title) AS title,
    TRIM(body)  AS body,
    loaded_at
FROM {{ source('staging', 'posts') }}
WHERE id IS NOT NULL
