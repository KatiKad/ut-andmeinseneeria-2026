# Praktikum 7: Andmeturve ja privaatsus (Edasijõudnud)

## Eesmärk

Rakendada rollipõhist ligipääsukontrolli (RBAC), andmete maskeerimist ja auditit dbt-projektis. Maskeerimisloogika on dbt-vaadetes inline, kasutades PostgreSQL `pg_has_role()` funktsiooni — üks vaade, mille sisu sõltub päringut tegevast rollist.

## Õpiväljundid

- Oskab kasutada `pg_has_role()` funktsiooni dünaamiliseks rollipõhiseks maskeerimiseks
- Mõistab kolme turvatehnikat: vaatepõhine maskeerimine, Row-Level Security, Column-Level GRANT
- Teab, kuidas seadistada pgAudit ja lugeda auditiloge

## Eeldused

- Praktikumide 3 ja 6 materjal on läbitud (pg-duckdb, dbt, medaljoniarhitektuur tuttav)
- Docker ja Docker Compose on paigaldatud
- Andmebaasiklient: psql (konteineris saadaval) või DBeaver / DataGrip

## Arhitektuur

```
staging skeema          intermediate (view)      marts (table)         secured (view)
  users (toorandmed)  ->  int_users           ->  dim_users         ->  vw_dim_users
  posts (toorandmed)  ->  int_posts           ->  fct_posts         ->  vw_fct_posts
                                                                    ->  dim_users_regional_base
                                                                        (RLS + col-grant)
```

**Põhiprintsiip:** üks turvavaade tabeli kohta. Kõik rollid teevad päringuid ühele ja samale `vw_dim_users`-le. Iga tulba CASE-avaldis kontrollib `pg_has_role()`-ga päringut tegevat rolli ja tagastab vastava versiooni: toorandmed, maskeeritud või NULL.

**Rollid ja kuvatav sisu `secured.vw_dim_users`-st:**

| Tulp           | `auditor`  | `analyst`        | `marketing` |
|----------------|------------|------------------|-------------|
| user_key       | toore      | toore            | toore       |
| first_name     | toore      | mask_varchar     | NULL        |
| last_name      | toore      | mask_varchar     | NULL        |
| full_name      | toore      | mask_varchar     | NULL        |
| email          | toore      | mask_email       | 'REDACTED'  |
| city           | toore      | mask_varchar     | toore       |
| country        | toore      | toore            | toore       |
| registered_date| toore      | mask_date        | mask_date   |

`regional_manager` ei kasuta `vw_dim_users`-i — pääseb ligi ainult `dim_users_regional_base` tabelile (RLS regiooni järgi + email-veerg keelatud).

## Kiirstart

```bash
# 1. Keskkond
cp .env.example .env
# Täida .env: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

# 2. Käivita konteinerid
docker compose up -d --build

# 3. Laadi andmed staging skeemasse
docker compose exec python python ingest.py users
docker compose exec python python ingest.py posts

# 4. Loo andmebaasi rollid
docker compose exec dbt dbt run-operation create_roles

# 5. Ehita kõik mudelid
docker compose exec dbt dbt run

# 6. Ava psql
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## Demo

### 1. Üks vaade, kolm rollipõhist sisu — `pg_has_role()`

Ava [vw_dim_users.sql](dbt_project/models/secured/vw_dim_users.sql):

```sql
SELECT
    user_key,
    user_id,

    CASE
        WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN email
        WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_email('email') }}
        ELSE 'REDACTED'
    END AS email,

    -- ... sama mall iga PII-tulba kohta
FROM {{ ref('dim_users') }}
```

`pg_has_role(current_user, 'auditor', 'MEMBER')` tagastab `true`, kui päringut tegev kasutaja on `auditor` rolli liige (sh kui `SET ROLE auditor` on tehtud). PostgreSQL hindab CASE iga rea kohta.

Vaate loomisel rakendub automaatselt dbt grants config:

```sql
-- vw_dim_users.sql
{{ config(grants={'select': ['analyst', 'marketing', 'auditor']}) }}
```

Maskeerimisfunktsioonid ([macros/masking.sql](dbt_project/macros/masking.sql)):

```
mask_email('juhan.tamm@gmail.com')  ->  'j***@gmail.com'
mask_varchar('Tallinn')             ->  'T******'
mask_date('2019-07-15')             ->  '2019-07-01'
```

### 2. Demo: kolme rolli päring samale vaatele

```sql
-- Auditor naeb toorandmeid
SET ROLE auditor;
SELECT first_name, email, city FROM secured.vw_dim_users LIMIT 3;
-- 'Juhan' | 'juhan@example.com' | 'Tallinn'

-- Analuutik naeb maskeeritud
RESET ROLE; SET ROLE analyst;
SELECT first_name, email, city FROM secured.vw_dim_users LIMIT 3;
-- 'J****' | 'j***@example.com' | 'T******'

-- Turundus ei nae PII-d
RESET ROLE; SET ROLE marketing;
SELECT first_name, email, city FROM secured.vw_dim_users LIMIT 3;
-- NULL    | 'REDACTED'        | 'Tallinn'
RESET ROLE;
```

### 3. Row-Level Security: `dim_users_regional_base`

`dim_users_regional_base` ([secured/dim_users_regional_base.sql](dbt_project/models/secured/dim_users_regional_base.sql)) on tabel (mitte vaade), kus `post_hook` rakendab RLS-poliitika:

```sql
ALTER TABLE secured.dim_users_regional_base ENABLE ROW LEVEL SECURITY;
CREATE POLICY region_isolation ON secured.dim_users_regional_base
    FOR SELECT TO regional_manager
    USING (country = current_setting('app.current_region', true));
```

Demo:

```sql
SET ROLE regional_manager;

-- Ilma regiooni seadmiseta: tuhi tulemus (turvaline vaikekaitumine)
SELECT country, city FROM secured.dim_users_regional_base;
-- (0 rows)

SET app.current_region = 'Finland';
SELECT country, city FROM secured.dim_users_regional_base;
-- Naitab ainult Soome kasutajaid

SET app.current_region = 'Germany';
SELECT country, city FROM secured.dim_users_regional_base;
-- Naitab ainult Saksamaa kasutajaid

RESET ROLE;
```

### 4. Column-Level GRANT: keelatud veerg

Sama `dim_users_regional_base` post_hook annab `regional_manager`-ile GRANT-i ainult valitud veergudele:

```sql
GRANT SELECT (user_key, user_id, first_name, last_name, full_name, city, country, registered_date)
    ON secured.dim_users_regional_base TO regional_manager;
-- email-veergu pole nimekirjas
```

```sql
SET ROLE regional_manager;
SET app.current_region = 'Estonia';

SELECT first_name, city FROM secured.dim_users_regional_base;
-- Toimib

SELECT email FROM secured.dim_users_regional_base;
-- ERROR: permission denied for column "email"

RESET ROLE;
```

Vaata column-tasandi grants süsteemikataloogist:

```sql
SELECT grantee, column_name, privilege_type
FROM information_schema.column_privileges
WHERE table_schema = 'secured'
  AND table_name = 'dim_users_regional_base'
ORDER BY column_name;
```

### 5. pgAudit: kes mida päris

Ava teises terminalis auditilogi jälgimine:

```bash
docker logs -f praktikum-db-07 2>&1 | grep AUDIT
```

Tee päringuid (esimeses terminalis):

```sql
SET ROLE analyst;   SELECT email FROM secured.vw_dim_users LIMIT 1; RESET ROLE;
SET ROLE marketing; SELECT * FROM secured.vw_dim_users LIMIT 1;     RESET ROLE;
SET ROLE auditor;   SELECT email FROM marts.dim_users LIMIT 1;      RESET ROLE;
```

Logis ilmub iga päringu kohta rida formaadis:

```
AUDIT: SESSION,1,1,READ,SELECT,VIEW,secured.vw_dim_users,"SELECT email ...",<none>
```

Väljad: `AUDIT: SESSION, statement_id, substatement_id, class, command, object_type, object_name, statement, parameters`.

pgAudit logib (vt seadistust [compose.yml](compose.yml) `-c` parameetritest):
- `READ` — SELECT-laused (sh mis tabelist/vaatest)
- `WRITE` — INSERT/UPDATE/DELETE
- `ROLE` — GRANT/REVOKE/CREATE ROLE
- `DDL` — CREATE/DROP/ALTER

## Ülesanded

### Ülesanne 1: Uus roll `finance_analyst`

Finantsosakond soovib näha postituste statistikat ja kasutajate registreerumiskuud, kuid mitte nimesid, e-posti ega linnu.

**Samm 1.** Lisa `finance_analyst` `macros/roles.sql` `create_roles` makro ARRAY-i ja käivita:
```bash
docker compose exec dbt dbt run-operation create_roles
```

**Samm 2.** Muuda `vw_dim_users.sql` ja `vw_fct_posts.sql`:
- Lisa `finance_analyst` `grants.select` listi
- Lisa igale CASE-avaldisele `finance_analyst` haru — kas NULL (PII) või toore väärtus (mitte-PII)

Näide email-veerule:
```sql
CASE
    WHEN pg_has_role(current_user, 'auditor', 'MEMBER') THEN email
    WHEN pg_has_role(current_user, 'analyst', 'MEMBER') THEN {{ mask_email('email') }}
    WHEN pg_has_role(current_user, 'finance_analyst', 'MEMBER') THEN NULL
    ELSE 'REDACTED'
END AS email
```

**Samm 3.** Käivita `dbt run --select secured` ja kontrolli:
```sql
SET ROLE finance_analyst;
SELECT * FROM secured.vw_dim_users LIMIT 3;
-- email peab olema NULL, country peab olema toore
RESET ROLE;
```

### Ülesanne 2: RLS keerulisema tingimusega

Lisa uus RLS-tabel `secured.fct_posts_short`, mis näitab `analyst`-rollile ainult lühikesi postitusi (`body_length < 200`).

**Samm 1.** Loo uus mudel `models/secured/fct_posts_short.sql` materializatsioon `table`, valides kõik `fct_posts` veerud.

**Samm 2.** Lisa post_hook makro analoogiliselt `enable_rls_by_region`-iga (vt [macros/rls.sql](dbt_project/macros/rls.sql)):

```sql
ALTER TABLE {{ this }} ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS short_posts_only ON {{ this }};
CREATE POLICY short_posts_only ON {{ this }}
  FOR SELECT TO analyst
  USING (body_length < 200);
```

**Samm 3.** Käivita `dbt run --select secured.fct_posts_short` ja testi:
```sql
SET ROLE analyst;
SELECT MIN(body_length), MAX(body_length) FROM secured.fct_posts_short;
-- max peab olema < 200
```

### Ülesanne 3: Auditilogi analüüs

Tee järgmised päringud erinevate rollidega ja analüüsi pgAudit logi:

```sql
SET ROLE analyst;   SELECT email FROM secured.vw_dim_users; RESET ROLE;
SET ROLE marketing; SELECT * FROM secured.vw_dim_users;      RESET ROLE;
SET ROLE auditor;   SELECT * FROM marts.dim_users LIMIT 1;   RESET ROLE;
```

Kogu logid ja vasta küsimustele:
```bash
docker compose logs db 2>&1 | grep "AUDIT" > /tmp/audit.log
```

1. Kuidas erineb logirida `analyst` ja `auditor` rollidega tehtud päringutele?
2. Kuidas tuvastada audiitorlogist päringud, mis puudutasid `email`-veergu?
3. Kas pgAudit logib SELECT-i tulemusi (read) või ainult lauset?

## Tõrkeotsing

### pgAudit extension ei aktiveeru

**Sümptom:** `dbt run` annab vea `could not open extension control file ".../pgaudit.control"`

**Diagnoos:** pgaudit pakett pole installitud:
```bash
docker compose exec db apt list --installed 2>/dev/null | grep pgaudit
```

**Lahendus:** Kontrolli, et `Dockerfile.db` ehitamine õnnestus:
```bash
docker compose build db
docker compose up -d db
```

Kui `postgresql-18-pgaudit` paketti ei leia repodest, kommenteeri välja `on-run-start` hook `dbt_project.yml`-is. Praktikum töötab ka ilma pgAudit-ita.

### `pg_has_role` annab vea: roll ei eksisteeri

**Lahendus:** Käivita rollide loomine enne `dbt run`:
```bash
docker compose exec dbt dbt run-operation create_roles
```

### `permission denied for schema secured`

**Sümptom:**
```
SET ROLE analyst;
SELECT * FROM secured.vw_dim_users;
-- ERROR: permission denied for schema secured
```

**Põhjus:** dbt `grants` config annab `SELECT`-õiguse ainult objektile, mitte skeemale. Rollil pole `USAGE` õigust skeemale `secured`.

**Lahendus:** `dbt run` lõpus käivitub `on-run-end` hook ([dbt_project.yml](dbt_project/dbt_project.yml)) mis annab vajaliku USAGE-õiguse:
```sql
GRANT USAGE ON SCHEMA secured TO analyst, marketing, regional_manager, auditor;
```

Kui sa nägid seda viga, käivita `dbt run` uuesti — `on-run-end` käivitub iga `dbt run` lõpus. Või anna käsitsi:
```sql
GRANT USAGE ON SCHEMA secured TO analyst, marketing, auditor;
```

### RLS ei filtreeri

**Sümptom:** `SET ROLE regional_manager` + `SELECT * FROM secured.dim_users_regional_base` tagastab kõik read

**Lahendus:** Käivita `dbt run --select secured.dim_users_regional_base` — `post_hook` loob poliitika uuesti.
