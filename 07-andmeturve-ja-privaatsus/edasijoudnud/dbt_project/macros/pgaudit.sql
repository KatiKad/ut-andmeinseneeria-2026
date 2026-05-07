-- pgAudit extension-i aktiveerimine
-- Kutsutakse automaatselt on-run-start hookist (dbt_project.yml)
-- Eeldab et postgresql-18-pgaudit on installitud (Dockerfile.db)
-- ja shared_preload_libraries sisaldab 'pgaudit' (compose.yml command)

{% macro ensure_pgaudit_extension() %}
  {% if execute %}
    {% do run_query("CREATE EXTENSION IF NOT EXISTS pgaudit") %}
    {% do log('pgAudit extension aktiveeeritud', info=true) %}
  {% endif %}
{% endmacro %}
