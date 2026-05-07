-- Maskeerimise makrod: iga funktsioon vastab ühele meta.mask väärtusele
-- Kasutamine: {{ mask_email('email') }} AS email

{% macro mask_email(col) %}
  left({{ col }}, 1) || '***@' || split_part({{ col }}, '@', 2)
{% endmacro %}

-- Säilitab esimese tähe, asendab ülejäänud tärnidega: "Juhan" -> "J****"
{% macro mask_varchar(col) %}
  left({{ col }}, 1) || repeat('*', greatest(length({{ col }}) - 1, 0))
{% endmacro %}

-- Trunkeerib kuupäeva kuu algusesse: "2023-07-15" -> "2023-07-01"
{% macro mask_date(col) %}
  date_trunc('month', {{ col }})::date
{% endmacro %}

-- Ümardab täisarvu lähima 1000-ni alla: 12345 -> 12000
{% macro mask_int(col) %}
  (floor({{ col }}::numeric / 1000) * 1000)::int
{% endmacro %}

-- Asendab väärtuse NULL-iga (veerg on nähtav aga tühi)
{% macro mask_null(col) %}
  NULL
{% endmacro %}
