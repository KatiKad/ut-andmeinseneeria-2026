-- Row-Level Security (RLS) makrod
--
-- RLS piirab milliseid ridu konkreetne roll naeb.
-- Poliitika USING-klausel arvutatakse iga päringu real eraldi.
-- current_setting('app.current_region', true) loeb seansi-tasandi muutuja:
--   SET app.current_region = 'Estonia';
-- Kui muutuja pole seatud, tagastab NULL -> ükski rida ei läbi filtrit (turvaline vaike).
--
-- Kasutamine post_hook-is:
--   post_hook: "{{ enable_rls_by_region(this, region_col='country') }}"

{% macro enable_rls_by_region(relation, region_col='country') %}
  ALTER TABLE {{ relation }} ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS region_isolation ON {{ relation }};
  CREATE POLICY region_isolation ON {{ relation }}
    FOR SELECT
    TO regional_manager
    USING ({{ region_col }} = current_setting('app.current_region', true));
{% endmacro %}
