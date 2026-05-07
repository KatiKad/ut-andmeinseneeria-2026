-- Lühike kokkuvõte sellest, millised reeglid kõige rohkem ridu mõjutavad.

SELECT
    rule_name,
    COUNT(*) AS failed_rows
FROM {{ ref('order_rule_results') }}
GROUP BY rule_name
ORDER BY failed_rows DESC, rule_name
