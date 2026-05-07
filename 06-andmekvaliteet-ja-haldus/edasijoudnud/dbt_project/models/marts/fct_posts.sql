-- Postituste faktitabel koos kasutajadimensiooniga
-- intermediate (hõbe) -> marts (kuld)

SELECT
    p.post_id,
    u.user_key,
    u.full_name         AS author_name,
    p.title,
    p.body,
    LENGTH(p.body)      AS body_length,
    p.loaded_at
FROM {{ ref('int_posts') }} p
LEFT JOIN {{ ref('dim_users') }} u
    ON p.user_id = u.user_id
