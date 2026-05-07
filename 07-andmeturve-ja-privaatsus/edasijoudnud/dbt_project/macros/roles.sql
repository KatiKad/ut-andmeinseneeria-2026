-- Rollide haldus
-- Kasutamine: dbt run-operation create_roles

{% macro create_roles() %}
  {% set sql %}
    DO $$
    DECLARE r TEXT;
    BEGIN
      FOREACH r IN ARRAY ARRAY['analyst', 'marketing', 'regional_manager', 'auditor'] LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
          EXECUTE format('CREATE ROLE %I', r);
          RAISE NOTICE 'Loodud roll: %', r;
        ELSE
          RAISE NOTICE 'Roll on juba olemas: %', r;
        END IF;
      END LOOP;
    END $$;
  {% endset %}
  {% do run_query(sql) %}
  {% do log('Rollid kontrollitud/loodud: analyst, marketing, regional_manager, auditor', info=true) %}
{% endmacro %}


{% macro drop_roles() %}
  {% set sql %}
    DO $$
    DECLARE r TEXT;
    BEGIN
      FOREACH r IN ARRAY ARRAY['analyst', 'marketing', 'regional_manager', 'auditor'] LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
          EXECUTE format('DROP ROLE %I', r);
          RAISE NOTICE 'Kustutatud roll: %', r;
        END IF;
      END LOOP;
    END $$;
  {% endset %}
  {% do run_query(sql) %}
  {% do log('Rollid kustutatud', info=true) %}
{% endmacro %}
