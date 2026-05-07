-- Puhastatud tellimuste hulgas ei tohi olla ridu, mis jäid kvaliteeditestides hätta.

SELECT
    c.staging_row_id
FROM {{ ref('orders_clean') }} AS c
INNER JOIN {{ ref('order_rule_results') }} AS r
    ON c.staging_row_id = r.staging_row_id
