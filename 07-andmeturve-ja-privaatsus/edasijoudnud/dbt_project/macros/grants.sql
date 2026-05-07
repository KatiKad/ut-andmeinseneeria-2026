-- Veerupohine ligipaasukonttroll (Column-Level Security)
--
-- REVOKE ALL eemaldab tabeli-tasandi SELECT-oiguse.
-- GRANT SELECT (col1, col2) annab oiguse ainult loetelud veergudele.
-- Tulemus: SELECT email FROM tabel WHERE rollil pole email-i oigust
--          -> ERROR: permission denied for column "email"
--
-- Kasutamine post_hook-is:
--   post_hook: "{{ grant_column_level(this, role='regional_manager',
--                   columns=['user_key', 'first_name', 'city', 'country']) }}"

{% macro grant_column_level(relation, role, columns) %}
  GRANT USAGE ON SCHEMA {{ relation.schema }} TO {{ role }};
  REVOKE ALL ON {{ relation }} FROM {{ role }};
  GRANT SELECT ({{ columns | join(', ') }}) ON {{ relation }} TO {{ role }};
{% endmacro %}


-- Skeem-tasandi USAGE oiguse andmine rollile
{% macro grant_schema_usage(schema_name, roles) %}
  {% for role in roles %}
    GRANT USAGE ON SCHEMA {{ schema_name }} TO {{ role }};
  {% endfor %}
{% endmacro %}
