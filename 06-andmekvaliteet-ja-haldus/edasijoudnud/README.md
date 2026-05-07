# Praktikum 6: Andmekvaliteet ja andmehaldus — OpenMetadata (edasijõudnud)

## Eesmärk

Ühendada andmeplatvorm (PostgreSQL + dbt) andmehalduse platvormiga (OpenMetadata). Praktikumi lõpuks oskad seadistada metaandmete kogumist, klassifitseerida andmeid, jälgida andmete pärinevust ja käivitada andmekvaliteedi teste tsentraalsest andmekataloogist.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Käivitab OpenMetadata instantsi Docker Compose abil ja orienteerub kasutajaliideses
- Seadistab andmeallika ühenduse (PostgreSQL) ja käivitab metadata ingestion pipeline'i
- Klassifitseerib andmeid (sildid, sõnastiku terminid, PII märgistamine)
- Uurib ja tõlgendab andmepärinevust (lineage) automaatselt tuletatud graafist
- Defineerib ja käivitab andmekvaliteedi teste (Data Quality test suite)
- Seob dbt projekti metaandmed OpenMetadataga (dbt ingestion)

## Ülevaade

| Osa | Sisu |
|-----|------|
| Ettevalmistus | Keskkonna käivitamine, andmete laadimine, dbt mudelite ehitamine |
| 1. samm | OpenMetadata kasutajaliidese tutvustus |
| 2. samm | PostgreSQL ühendamine ja metadata ingestion |
| 3. samm | Andmete klassifitseerimine: sildid, sõnastik, PII |
| 4. samm | Andmepärinevus (lineage) |
| 5. samm | Andmekvaliteedi testid OpenMetadatas |
| 6. samm | dbt metaandmete sidumine OpenMetadataga |

---

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Kogemus PostgreSQL, SQL ja Pythoniga
- dbt põhitõed praktikumist 3
- Eelmiste praktikumide konteinerid on peatatud (`docker compose down`)
- **Minimaalselt 8 GB RAM** — OpenMetadata koos Elasticsearch ja Airflowiga vajab märkimisväärset mälumahtu

## Miks on see teema oluline?

Andmete kogumine ja teisendamine on vaid pool tööd. Kui keegi küsib „kust see arv tuleb?", „kas neid andmeid tohib kasutada?" või „millal viimati uuendati?", peab vastus olema kiiresti leitav. Andmekataloog on tsentraalne koht, kus metaandmed, omanikud, kvaliteedikontrollid ja pärinevus on koos.

OpenMetadata on avatud lähtekoodiga platvorm, mis ühendab need võimekused ühte kohta. See ei asenda dbt teste ega Airflow töövoogusid — see täiendab neid, pakkudes ühtset pilti kogu andmeplatvormist.

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **OpenMetadata** | Avatud lähtekoodiga andmekataloog ja metaandmete halduse platvorm. Koondab andmeallikad, skeemad, kirjeldused, kvaliteedikontrollid ja pärinevuse ühte kasutajaliidesse. |
| **Metadata Ingestion (Agents)** | Automaatne metaandmete kogumine andmeallikatest. OpenMetadata ühendub andmebaasiga ja tõmbab välja skeemad, tabelid, veerud ja nende omadused. |
| **Data Lineage** | Andmete pärinevus — visuaalne ülevaade, kust andmed tulevad, milliseid teisendusi läbivad ja kuhu jõuavad. |
| **Business Glossary** | Ärisõnastik — ühised terminid ja definitsioonid, mis seovad ärikeele tehniliste andmevaradega. |
| **PII (Personally Identifiable Information)** | Isikuandmed — andmed, mille kaudu saab isikut tuvastada (nimi, e-post, aadress jne). Vajavad erilist kaitset. |
| **Data Profiling** | Andmete profileerimine — automaatne statistika kogumine veergude kohta (tühjad väärtused, unikaalsed väärtused, jaotus jms). |
| **Data Quality Test Suite** | Andmekvaliteedi testide kogum — reeglid, mis kontrollivad andmete vastavust ootustele (unikaalsus, tühjuse puudumine, vahemikud). |
| **Data Owner** | Äripool, kes vastutab andmekogu eest ja määrab ligipääsureeglid. |
| **Data Steward** | Isik, kes hoolitseb andmekvaliteedi ja dokumentatsiooni eest. |

---

## Keskkond

### Teenused

| Teenus | Konteiner | Kirjeldus |
|--------|-----------|-----------|
| PostgreSQL | `praktikum-db-06` | Andmebaas (pgduckdb) — meie andmeladu |
| Python | `praktikum-python-06` | Andmete laadimine API-st |
| dbt | `praktikum-dbt-06` | SQL-transformatsioonid (medaljonarhitektuur) |
| OpenMetadata Server | `openmetadata_server` | Andmekataloogi kasutajaliides ja API |
| OMD Ingestion | `openmetadata_ingestion` | Airflow-põhised ingestion pipeline'id |
| OMD MySQL | `openmetadata_mysql` | OpenMetadata sisemine metaandmete hoidla |
| OMD Elasticsearch | `openmetadata_elasticsearch` | Otsinguindeks andmekataloogi jaoks |

### Seadistamine

1. Kopeeri `.env.example` failist `.env`:

```bash
cp .env.example .env
```

2. Vajadusel muuda `.env` failis kasutajanimed ja paroolid.

> **NB!** `.env` fail sisaldab paroole ja **ei tohi** satuda Giti repositooriumisse. Fail on lisatud `.gitignore`-sse.

3. Käivita teenused:

```bash
docker compose up -d --build
```

> **NB!** OpenMetadata käivitumine võtab **2–4 minutit** (migratsioon, Elasticsearch, Airflow). Ära muretse, kui `execute_migrate_all` konteiner esialgu töötab — see on ühekordne initsialiseerimise samm.

4. Kontrolli, et kõik teenused töötavad:

```bash
docker compose ps
```

Oodatav tulemus: `praktikum-db-06`, `praktikum-python-06`, `praktikum-dbt-06`, `openmetadata_server`, `openmetadata_ingestion`, `openmetadata_mysql`, `openmetadata_elasticsearch` on olekus `running` (või `Up`). Konteiner `execute_migrate_all` peaks olema olekus `exited (0)` — see on normaalne.

### Ühendused

| Teenus | Kasutaja | Parool | Port / URL |
|--------|----------|--------|------------|
| PostgreSQL | `praktikum` | `praktikum` | localhost:5432 |
| OpenMetadata | `andmeinsener@admin.ee` | `admin` (muuda esimesel sisselogimisel) | http://localhost:8585 |
| Airflow (OMD) | `admin` | `admin` | http://localhost:8080 |

---

## Ettevalmistus: andmete laadimine ja dbt mudelite ehitamine (~10 min)

Enne OpenMetadata seadistamist peab andmebaasis olema sisu, mida kataloogida.

### 1. Laadi andmed API-st PostgreSQL-i

```bash
docker compose exec python python ingest.py users
docker compose exec python python ingest.py posts --batch 1
docker compose exec python python ingest.py posts --batch 2
```

Kontrolli tulemust:

```bash
docker compose exec db psql -U praktikum -c "SELECT COUNT(*) FROM staging.users;"
docker compose exec db psql -U praktikum -c "SELECT COUNT(*) FROM staging.posts;"
```

Oodatav tulemus: 10 kasutajat, 100 postitust.

### 2. Käivita dbt mudelid ja testid

```bash
docker compose exec dbt dbt run
docker compose exec dbt dbt test
docker compose exec dbt dbt snapshot
docker compose exec dbt dbt docs generate
```

> **Miks kirjeldused on kohe näha?** Projekt kasutab [`persist_docs`](https://docs.getdbt.com/reference/resource-configs/persist_docs) seadistust — `dbt run` kirjutab `schema.yml` kirjeldused PostgreSQL-i objektivarustusse (`COMMENT ON TABLE/COLUMN`). Metadata ingestion (samm 2) loeb need kommentaarid automaatselt. Samm 6 (dbt ingestion) lisab hiljem lineage'i ja testitulemused, mida objektivarustusse ei salvestata.

Kontrolli, et kõik mudelid ehitati ja testid läbiti:

```bash
docker compose exec db psql -U praktikum -c "\dt marts.*"
docker compose exec db psql -U praktikum -c "\dv intermediate.*"
```

Oodatav tulemus: marts skeemas tabelid `dim_users`, `fct_posts`, `user_post_summary`; intermediate skeemas vaated `int_users`, `int_posts`.

### 3. Kontrolli, et OpenMetadata on käivitunud

Ava brauseris http://localhost:8585. Peaks avanema OpenMetadata sisselogimisleht.

> Kui leht ei avane, kontrolli `docker compose logs openmetadata-server --tail=20`. Levinuim põhjus: migratsioon pole veel lõppenud. Oota veel 1–2 minutit.

**Kontrollpunkt 0:** kõik teenused töötavad, andmebaasis on andmed neljas skeemas (staging, intermediate, marts, snapshots), OpenMetadata kasutajaliides avaneb brauseris.

---

## 1. samm: OpenMetadata kasutajaliidese tutvustus (~5 min)

Logi OpenMetadata kasutajaliidesse sisse:

- **Kasutajanimi:** `andmeinsener@admin.ee`
- **Parool:** `admin`

Esimesel sisselogimisel muuda parool: **Settings → Users → andmeinsener → Change Password** → sisesta uueks parooliks `praktikum`. Paroolipõhise autentimise dokumentatsioon: https://docs.open-metadata.org/deployment/security/basic-auth

> **Tootmiskeskkonnas** on turvalisem ja tavapärasem kasutada organisatsiooni olemasolevat kasutajahalduse lahendust (nt Azure SSO, Okta, Google SSO). Paroolipõhine `basic-auth` sobib praktikumikeskkonnale, kuid ei ole soovitatav tootmises.

### Kasutajaliidese struktuur

Tutvu vasakpoolse menüü põhipunktidega:

| Menüüpunkt | Kirjeldus |
|------------|-----------|
| **Home** | Avaleht: viimased tegevused ja kiirviited |
| **Explore** | Kõik registreeritud andmevarad (tabelid, vaated, torujuhtmed) — peamine koht andmete leidmiseks |
| **Lineage** | Andmepärinevuse graafik kogu platvormi lõikes |
| **Observability** | Andmete tervise jälgimine: kvaliteedikontrollid, teavitused, reeglid |
| **Insights** | Andmeplatvormi kasutusstatistika ja ülevaated |
| **Domains** | Ärivaldkondade haldamine — andmevarade rühmitamine ärikonteksti järgi |
| **Govern** | Andmehaldus: ärisõnastik (Glossary), klassifikaatorid, põhimõtted |
| **Settings** | Teenuste haldamine, kasutajad, ingestion seadistused |

### OpenMetadata arhitektuur

OpenMetadata koosneb mitmest komponendist:

| Komponent | Konteiner | Roll |
|-----------|-----------|------|
| **Server** | `openmetadata_server` | Põhirakendus: API, kasutajaliides, äriloogika |
| **Ingestion** | `openmetadata_ingestion` | Airflow-põhised torujuhtmed metaandmete kogumiseks |
| **MySQL** | `openmetadata_mysql` | Metaandmete salvestamine (OpenMetadata enda andmed) |
| **Elasticsearch** | `openmetadata_elasticsearch` | Andmevarade otsingufunktsionaalsus |

> NB! OpenMetadata MySQL ei ole sama asi mis meie PostgreSQL andmeladu. MySQL on OpenMetadata sisemine andmebaas, kuhu salvestatakse metaandmed, kirjeldused, testide tulemused jm. PostgreSQL on meie andmeladu, mille sisu me kataloogime.

**Kontrollpunkt 1:** oled sisseloginud, tutvunud kasutajaliidese struktuuriga ja mõistad, millist rolli iga OpenMetadata komponent täidab.

---

## 2. samm: PostgreSQL andmeallika ühendamine ja metadata ingestion (~15 min)

Selles sammus ühendame oma PostgreSQL andmelao OpenMetadataga ja käivitame automaatse metaandmete kogumise.

### Andmeallika lisamine

1. Mine **Settings** → **Services** → **Databases**
2. Klõpsa **Add New Service**
3. Vali teenuse tüüp: **Postgres**
4. Täida ühenduse andmed:
   - **Name:** `praktikum_andmeladu`
   - **Host and Port:** `db:5432` (Docker teenuse nimi, mitte localhost)
   - **Username:** `.env` failis määratud kasutajanimi (vaikimisi `praktikum`)
   - **Password:** `.env` failis määratud parool (vaikimisi `praktikum`)
   - **Database:** `.env` failis määratud andmebaasi nimi (vaikimisi `praktikum`)

5. Klõpsa **Test Connection**

Oodatav tulemus: kõik kontrollid (Database, Schemas, Tables, Views) on rohelised.

6. Klõpsa **Save**

> **Tõrkeotsing — GetQueries näitab viga `pg_stat_statements does not exist`:**
> - **Sümptom:** Test Connection tulemuses on enamik kontrolle rohelised, aga `GetQueries` näitab viga.
> - **Põhjus:** OpenMetadata proovib kontrollida SQL-päringute logimist, mis nõuab PostgreSQL laiendust `pg_stat_statements`. See pole vaikimisi lubatud.
> - **Lahendus:** ignoreeri seda viga — see mõjutab ainult päringute kasutusstatistika kogumist (Usage ingestion), mitte tabeli- ja veergude metaandmete kogumist (Metadata ingestion). Klõpsa **Save** ja jätka.

> **Tõrkeotsing — Test Connection ebaõnnestub täielikult:**
> - **Sümptom:** ühenduse test näitab punast (mitte ainult GetQueries).
> - **Diagnostika:** kontrolli, et PostgreSQL konteiner töötab (`docker compose ps`) ja et kasutajanimi/parool vastavad `.env` failis olevatele väärtustele.
> - **Lahendus:** kasuta hosti `db` (mitte `localhost`). OpenMetadata ingestion konteiner asub samas Docker võrgus ja ühendub teenuse nime kaudu.

### Metadata Ingestion pipeline (Agent) käivitamine

Juhul kui automaatselt pole loodud Metadata Agent, siis tee järgmised sammud:

> Pärast teenuse salvestamist suunatakse sind ingestion seadistuse (Agents) lehele.
> 
> 1. Vali **Add Agent** → **Add Metadata Agent**
> 2. Jäta vaikeseadistused (kõik skeemad, kõik tabelid)
> 3. Klõpsa **Submit**
> 
> Pipeline käivitub automaatselt. Oodatav kestus: 30–60 sekundit.

4. Kontrolli tulemust: mine **Explore** → **Tables**

Peaksid nägema oma andmebaasi tabeleid ja vaateid:

| Skeema | Tabelid/vaated |
|--------|----------------|
| staging | users, posts, etl_log |
| intermediate | int_users (vaade), int_posts (vaade) |
| marts | dim_users, fct_posts, user_post_summary |
| snapshots | snap_users |

5. Klõpsa mõnel tabelil (nt `marts.dim_users`) ja uuri veergude infot — pane tähele, et dbt `schema.yml` kirjeldused on juba nähtavad (`persist_docs` kaudu PostgreSQL-i kommentaaridest loetud)

> **Arhitektuuriotsus:**
>
> 1. **Probleem.** Kuidas saab OpenMetadata teada, millised tabelid ja veerud meie andmebaasis on?
> 2. **Variandid.** (a) Käsitsi registreerimine — igale tabelile ja veerule tuleb manuaalselt kirje luua. (b) Automaatne ingestion pipeline — ühendub andmebaasiga ja tõmbab metaandmed välja. (c) API-põhine import — kolmanda osapoole tööriist saadab metaandmed OMD API kaudu.
> 3. **Valik ja põhjendus.** Automaatne ingestion pipeline, sest see skaleerub: kümned tabelid täna, sajad homme. Käsitsi registreerimine on veaohtlik ja aeglane.
> 4. **Kompromissid.** Automatiseerimine impordib kõik, sh ajutised ja test-tabelid. Tootmiskeskkonnas tasub filtreerida, millised skeemad importida.

**Kontrollpunkt 2:** OpenMetadata näitab kõiki nelja skeema tabeleid ja vaateid. Saad uurida veergude nimesid ja tüüpe.

---

## 3. samm: Andmete klassifitseerimine (~20 min)

Metaandmete kogumine on alles algus. Tabelid ja veerud on näha, aga keegi ei tea, mida need tähendavad ja millised neist sisaldavad tundlikke andmeid. Selles sammus lisame andmevaradele kirjeldused, sildid ja sõnastiku terminid.

### Osa A: Isikuandmete (PII) märgistamine siltidega

Isikuandmed on andmed, mille kaudu saab isikut tuvastada: nimi, e-posti aadress, aadress jne. Need vajavad erilist kaitset (GDPR, isikuandmete kaitse seadus).

1. Mine **Explore** → vali tabel `praktikum_andmeladu.praktikum.marts.dim_users`
2. Klõpsa veerule `email`
3. Lisa silt: klõpsa **Tags** väljal → otsi `PII` → vali `PII.Sensitive`
4. Korda sama järgmiste veergudega:
   - `full_name` → `PII.Sensitive`
   - `city` → `PII.NonSensitive` (asukoht üksinda ei tuvasta isikut, kuid kombinatsioonis teiste andmetega võib)

5. Ava ka tabel `staging.users` ja märgista sarnaselt: `first_name`, `last_name`, `email` → `PII.Sensitive`

> **Mõttekoht:** Miks märgistada PII nii staging kui marts kihis? Staging kihis on toorandmed, mis võivad lekke korral olla isegi ohtlikumad (vähem kontrollitud ligipääs). PII märgistus peab olema andmete kogu teekonnal.

### Osa B: Ärisõnastiku (Glossary) loomine

Ärisõnastik ühendab ärikeele ja tehnilise keele. Kui analüütik küsib „aktiivne kasutaja", peab olema üks koht, kus see termin on defineeritud ja seotud konkreetsete andmevaradega.

1. Mine **Govern** → **Glossary**
2. Klõpsa **Add Glossary**
   - **Name:** `Andmeinseneeria sõnastik`
   - **Description:** `Kursuse andmemudeli ärimõistete definitsioonid`

3. Lisa terminid (**Add Term**):

   **Termin 1: Kasutaja**
   - **Name:** `Kasutaja`
   - **Description:** `Registreeritud kasutaja, kellel on unikaalne UUID ja profiiliandmed. Vastab dim_users tabelile marts kihis.`
   - **Synonyms:** `User`, `Klient`

   **Termin 2: Postitus**
   - **Name:** `Postitus`
   - **Description:** `Kasutaja loodud tekstisisu koos pealkirja ja sisuga. Vastab fct_posts tabelile marts kihis.`

   **Termin 3: Isikuandmed**
   - **Name:** `Isikuandmed`
   - **Description:** `Andmed, mille kaudu saab füüsilist isikut otseselt või kaudselt tuvastada. Hõlmab nime, e-posti, aadressi jm. Reguleeritud GDPR-i ja Eesti isikuandmete kaitse seadusega.`
   - **Synonyms:** `PII`, `Personal Data`

4. Seo terminid andmevaradega:
   - Mine tagasi tabeli `marts.dim_users` juurde
   - Klõpsa tabeli nimel → **Glossary Terms** → lisa `Kasutaja`
   - Ava veerg `email` → lisa **Glossary Term** `Isikuandmed`

5. Kontrolli tulemust: mine tagasi **Glossary** vaatesse ja vaata, milliste andmevaradega on terminid seotud

### Osa C: Andmehalduse rollid

OpenMetadata võimaldab määrata tabelitele ja skeemadele omanikke.

1. Ava tabel `marts.dim_users`
2. Klõpsa **Owner** väljal → vali `admin`
3. Arutle: kes on andmete omanik (Data Owner) ja kes andmete haldur (Data Steward)?

| Roll | Vastutus | Näide |
|------|----------|-------|
| **Data Owner** | Otsustab, kes andmetele ligi pääseb. Äripool. | Turundusmeeskonna juht vastutab kliendiandmete eest |
| **Data Steward** | Hoolitseb andmekvaliteedi ja dokumentatsiooni eest. | Andmeinsener, kes kirjutab valideerimisreeglid |
| **Data Engineer** | Ehitab ja hooldab andmetorujuhtmeid. | Arendaja, kes kirjutas dbt mudelid |

**Kontrollpunkt 3:** vähemalt 3 veerul on PII sildid, sõnastikus on 2+ terminit, terminid on seotud andmevaradega, tabelile on määratud omanik.

---

## 4. samm: Andmepärinevus — lineage (~10 min)

Andmepärinevus näitab, kust andmed tulevad ja kuhu lähevad. See aitab vastata küsimustele:
- „Kust see arv tuleb?" — vaata ülesvoolu (upstream)
- „Mida see muudatus mõjutab?" — vaata allavoolu (downstream)

### Vaata praegust pärinevuse graafikut

1. Mine **Explore** → ava vaade `intermediate.int_posts`
2. Klõpsa ülaribalt **Lineage**

Praegu näed pärinevust, mille OpenMetadata tuletas PostgreSQL metaandmetest. PostgreSQL salvestab vaate definitsiooni SQL-ina, millest OMD suudab seosed automaatselt tuletada.

3. Uuri graafikut:
   - Millised tabelid on `int_posts` ülesvoolu (upstream)?
   - Klõpsa mõnel tabelil graafikus ja vaata selle detaile

4. Ava ka `intermediate.int_users` ja vaata selle lineage'i

> **Miks mitte `marts.fct_posts`?** Marts kihis on mudelid materaliseeritud **tabelitena** (`materialized: table`). Tabel on PostgreSQL jaoks tühi objekt — selles puudub SQL definitsioon, millest pärinevust tuletada. Ainult vaated (VIEW) säilitavad SQL definitsiooni. Täielik lineage, mis näitab kogu ref() ahelat staging → intermediate → marts, tekib alles 6. sammus dbt ingestion käivitamise järel.

### Pärinevuse väärtus praktikas

Kujuta ette: keegi muudab `staging.users` tabeli veeru `email` andmetüüpi. Lineage graaf näitab kohe, et see mõjutab:
- `intermediate.int_users` vaadet
- `marts.dim_users` tabelit
- `marts.fct_posts` tabelit (läbi JOIN-i)
- `marts.user_post_summary` tabelit

Ilma lineage'ita peaks keegi selle ahela käsitsi kokku panema.

**Kontrollpunkt 4:** näed `int_posts` lineage graafikut (vaate pärinevus tuletatud PostgreSQL-st), mõistad upstream/downstream kontseptsiooni ja oskad selgitada, miks marts kihis lineage praegu puudub.

---

## 5. samm: Andmekvaliteedi testid OpenMetadatas (~20 min)

dbt-s defineerisime andmekvaliteedi testid juba `schema.yml` failides (unique, not_null, relationships). Need testid töötavad ehitamise ajal — kui `dbt test` ebaõnnestub, tead kohe.

OpenMetadata andmekvaliteedi testid on teistsugused: need käivituvad **ajakavapõhiselt** ja kontrollivad andmeid, mis on juba tabelites. See on „teine kaitseliin" — jooksev vaatlus (observability), mitte ehitusaegsed kontrollid.

### Osa A: Andmete profileerimine

Profileerimine kogub automaatselt statistikat tabelite ja veergude kohta (ridade arv, unikaalsed väärtused, tühjad väärtused, min/max jms). See annab ülevaate andmete seisust enne testide seadistamist.

**Profiler agendi seadistamine:**

Profiler agent on eeltäidetud vaikeväärtustega loodud, kuid sisaldab klassifikatsioonifiltreid (Tier 1, Tier 2), mis takistavad kõigi tabelite profileerimist.

1. Mine **Settings** → **Services** → **Databases** → `praktikum` teenus
2. Klõpsa **Agents** sakki (üleval)
3. Leia olemasolev profiler agent → klõpsa hamburgeri-menüüs (⋮) **Edit**
4. Leia **Classification Filter Pattern** väli — eemalda sealt `Tier1` ja `Tier2` kirjed
5. Jäta kõik muud filter pattern väljad tühjaks (profileerime kõik skeemid ja tabelid)
6. Klõpsa **Save**
7. Käivita agent: hamburgeri-menüü → **Run** — võtab 10–30 sekundit

Logid näed: Agents vaates → agendi rea all **Logs** link → avaneb Airflow logi vaade.

> **Praktikumis profileerime kõik, kuid päriselus ei tee seda kunagi.** Profileerimine loeb iga tabeli iga veeru kõik väärtused — suurandmete puhul (miljonid read, sadakond tabelit) tähendab see tohutut andmebaasikoormust ja pilvekulu. Tootmiskeskkonnas defineeri kindlad filtrid (skeemid, tabelid) ja profileeri ainult ärikriitilised andmed.

**Tulemuste vaatamine:**

8. Mine **Explore** → `marts.fct_posts`
9. Klõpsa sakki **Data Observability** → **Column Profile**
10. Näed veergude statistikat: Null %, Unique %, Distinct %, Value Count
    - Tekstitüüpi veergudel (nt `body`, `author_name`) näed jaotusstatistikat
    - Arvtüüpi veergudel (nt `body_length`) näed lisaks min/max/keskmist — klõpsa veerul, et näha detailsemat graafikut

> Dokumentatsioon: [Profiler Workflow — UI Configuration](https://docs.open-metadata.org/how-to-guides/data-quality-observability/profiler/profiler-workflow#ui-configuration)

### Osa B: Andmekvaliteedi testide loomine

1. Mine `marts.fct_posts` → sakk **Data Observability** → nupp **Add** → **Test case**
2. Avaneb dialoog, kus valid esmalt testi taseme:
   - **Table Level** — test rakendub tervele tabelile
   - **Column Level** — test rakendub ühele veerule

**Tabelitasandi testid** (vali Table Level):
- **Select Test Type:** `Table Row Count to be Between` — seadista Min: `50`, Max: `200`

**Veerutasandi testid** (vali Column Level, seejärel vali veerg):
- Veerg `post_id` → **Column Values to be Unique**
- Veerg `post_id` → **Column Values to be Not Null**
- Veerg `user_key` → **Column Values to be Not Null** — igal postitusel peab olema autor
- Veerg `body_length` → **Column Values to be Between** — Min: `1` (tühjad sisu ei tohiks olla)

3. Lisa testid ka tabelile `marts.dim_users` (sama voog: Data Observability → Add → Test case):
   - Veerg `user_key` → **Column Values to be Unique**
   - Veerg `user_key` → **Column Values to be Not Null**
   - Veerg `email` → **Column Values to be Not Null**

4. Käivita testid: **Data Observability** → **Data Quality** → sakk **Pipelines** → pipeline rea lõpus **⋮** → **Run**

   > Testide lisamisel loob OpenMetadata automaatselt TestSuite pipeline'i. Vaikimisi on ajakava "iga päev kell 00:00" — käsitsi käivitamiseks kasuta **⋮ → Run**.

5. Vaata tulemusi: **Data Quality** → sakk **Test Cases** — iga test näitab staatust (Success / Failed) ja käivituse ajalugu

### Osa C: dbt testid vs OpenMetadata testid

| Omadus | dbt testid | OpenMetadata testid |
|--------|-----------|-------------------|
| **Millal käivituvad** | `dbt test` käsu peale (ehitusaeg) | Ajakavapõhiselt või käsitsi (jooksev vaatlus) |
| **Kes kasutab** | Andmeinsener (pipeline ehitaja) | Andmehaldur (Data Steward), äripool |
| **Ebaõnnestumine** | Blokeerib pipeline'i | Tekitab teavituse, ei blokeeri |
| **Definitsioon** | YAML failides (`schema.yml`) | OpenMetadata kasutajaliideses |
| **Ajalugu** | `target/run_results.json` | OpenMetadata andmebaasis, nähtav graafikuna |
| **Fookus ja eesmärk** |	Koodi valideerimine, viidete terviklikkus, äriloogika vastavus. | Andmete vaadeldavus (observability), mahu ja värskuse (SLA) anomaaliad.|
| **Ulatus** |	Piiratud rangelt dbt projektis defineeritud mudelitega. | Kogu andmekataloog, sealhulgas dbt-välised allikasüsteemid.|

> **Arhitektuuriotsus:**
>
> 1. **Probleem.** Kus peaksid andmekvaliteedi kontrollid elama — transformatsioonitööriistas (dbt) või andmehalduse platvormis (OpenMetadata)?
> 2. **Variandid.** (a) Ainult dbt testid — piisav väikese meeskonna jaoks, aga äripool ei näe tulemusi. (b) Ainult OMD testid — pole ehitusaegset kaitset. (c) Kihiline lähenemine — dbt testid kui pipeline'i valvurid, OMD testid kui jooksev vaatlus.
> 3. **Valik ja põhjendus.** Kihiline lähenemine. dbt testid püüavad vead enne, kui halvad andmed marts kihti jõuavad. OMD testid kontrollivad andmeid ajakava järgi ja teavitavad probleemidest ka neid, kes dbt-d ei kasuta.
> 4. **Kompromissid.** Mõni kontroll on dubleeritud (nt not_null). See on teadlik valik: eri sihtrühmad vajavad eri vaateid.

**Kontrollpunkt 5:** vähemalt 4 andmekvaliteedi testi on loodud ja käivitatud OpenMetadatas, tulemused on nähtavad testide ajaloos.

---

## 6. samm: dbt metaandmete sidumine OpenMetadataga (~15 min)

Siiani on OpenMetadata kogunud metaandmed otse PostgreSQL-ist: skeemad, tabelid, veerud. Kuid sellest jääb oluline info puudu: dbt mudelite kirjeldused, testide tulemused ja `ref()` põhine lineage.

OpenMetadata dbt ingestion pipeline loeb dbt artefaktid (`manifest.json`, `catalog.json`, `run_results.json`) ja rikastab kataloogi nende andmetega.

### dbt artefaktide kontroll

Enne ingestion seadistamist kontrolli, et dbt artefaktid on olemas:

```bash
docker compose exec ingestion bash -c "ls /dbt-artifacts/"
```

Oodatav tulemus: `manifest.json`, `catalog.json`, `run_results.json` ja muid faile. Need genereeriti ettevalmistuse sammus käsuga `dbt docs generate`.

> Kui failid puuduvad, käivita uuesti:
> ```bash
> docker compose exec dbt dbt docs generate
> ```

### dbt ingestion pipeline seadistamine

1. Mine **Settings** → **Services** → **Databases** → vali `praktikum_andmeladu`
2. Mine **Agents** → klõpsa **Add Agent** → vali **Add dbt Agent**
3. Seadista dbt allikas:
   - **dbt Configuration Source:** `Local Config`
   - **dbt Catalog File Path:** `/dbt-artifacts/catalog.json`
   - **dbt Manifest File Path:** `/dbt-artifacts/manifest.json`
   - **dbt Run Results File Path:** `/dbt-artifacts/run_results.json`

4. Klõpsa **Submit**

Pipeline käivitub. Oodatav kestus: 30–60 sekundit.

### Tulemuse kontrollimine

Pärast edukat dbt ingestion'it muutub kataloogis kolm asja:

#### 1. Lineage on nüüd täielik

Mine `marts.fct_posts` → **Lineage** ja vaata uuesti. Nüüd peaksid nägema kogu dbt `ref()` ahelat:

```
staging.users ──> int_users ──> dim_users ──> fct_posts
staging.posts ──> int_posts ──────────────/
```

See on märkimisväärne erinevus: PostgreSQL metaandmetest tuletatud lineage näitas ainult vaadete seoseid. dbt lineage näitab kogu transformatsiooniahela loogika, sõltumata materialiseerimise tüübist.

#### 2. Kirjeldused on imporditud

Mine tabelile `marts.dim_users` ja vaata veergude kirjeldusi. dbt `schema.yml` failides defineeritud kirjeldused peaksid olema nähtavad.

#### 3. dbt testide tulemused on nähtavad

Vaata tabelite **Data Quality** vaates — dbt testide tulemused ilmuvad koos OpenMetadata enda testidega.

**Kontrollpunkt 6:** dbt lineage on nähtav OpenMetadatas (täielik staging → intermediate → marts ahel), dbt kirjeldused on imporditud, dbt testide tulemused on nähtavad.

---

## Levinud vead ja tõrkeotsing

### OpenMetadata ei käivitu

**Sümptom:** `docker compose ps` näitab, et `openmetadata_server` taaskäivitub (restarting).

**Diagnostika:**
```bash
docker compose logs openmetadata-server --tail=50
docker compose logs execute-migrate-all --tail=50
```

**Lahendus:**
- Kui migratsioon ebaõnnestus, proovi: `docker compose down -v && docker compose up -d`
- Kui mälu ei piisa: kontrolli, et masinas on vähemalt 8 GB RAM. Sulge teised mahukad rakendused.

### Metadata ingestion ebaõnnestub

**Sümptom:** ingestion pipeline näitab punast staatust.

**Diagnostika:**
- Vaata pipeline'i logisid OpenMetadata kasutajaliideses (pipeline → Logs)
- Või kontrolli Airflow logisid: http://localhost:8080

**Lahendus:**
- Kontrolli, et PostgreSQL konteiner töötab: `docker compose ps`
- Kontrolli, et ühenduse andmed on õiged: host `db`, port `5432`
- Kontrolli, et andmebaasis on tabelid: `docker compose exec db psql -U praktikum -c "\dt staging.*"`

### dbt ingestion ei leia artefakte

**Sümptom:** dbt ingestion pipeline ebaõnnestub teatega „file not found".

**Diagnostika:**
```bash
docker compose exec ingestion bash -c "ls -la /dbt-artifacts/"
```

**Lahendus:**
- Kui kaust on tühi, käivita: `docker compose exec dbt dbt docs generate`
- Kontrolli, et `compose.yml` failis on volume mount: `./dbt_project/target:/dbt-artifacts:ro`

### Pordikonflikt

**Sümptom:** `docker compose up` annab vea `port already in use`.

**Lahendus:** peata eelmiste praktikumide konteinerid:
```bash
# Teistes praktikumikaustades:
docker compose down
```

Eriti port 5432 (PostgreSQL) ja 8080 (Airflow) on levinud konfliktikohad.

---

## Kokkuvõte

Selles praktikumis ühendasime andmeplatvormi (PostgreSQL + dbt) andmehalduse platvormiga (OpenMetadata):

1. **Metadata ingestion** — OpenMetadata avastas automaatselt kõik skeemad, tabelid ja veerud meie PostgreSQL andmelaost
2. **Andmete klassifitseerimine** — märgistasime isikuandmeid PII siltidega, lõime ärisõnastiku terminid ja sidusime need andmevaradega
3. **Andmepärinevus** — nägime, kuidas andmed liiguvad läbi medaljonarhitektuuri kihtide (staging → intermediate → marts)
4. **Andmekvaliteedi testid** — seadistasime jooksvad kvaliteedikontrollid lisaks dbt ehitusaegsetele testidele
5. **dbt integratsioon** — importisime dbt mudelite kirjeldused, testide tulemused ja lineage'i OpenMetadata kataloogi

Tulemus on terviklik andmehalduse voog, kus metaandmed, kvaliteedikontrollid, pärinevus ja dokumentatsioon on ühes kohas kättesaadavad kõigile meeskonnaliikmetele.

---

## Lisaharjutus: kohandatud dbt test ja uuesti importimine

### Ülesanne

Lisa dbt projekti uus kohandatud test, käivita see ja impordi tulemused OpenMetadata kataloogi.

### Sammud

1. Loo fail `dbt_project/tests/assert_no_orphan_posts.sql`:

```sql
-- Leia postitused, mille autorile dim_users tabelis vastet ei leita
SELECT p.*
FROM {{ ref('fct_posts') }} p
LEFT JOIN {{ ref('dim_users') }} u ON p.user_key = u.user_key
WHERE u.user_key IS NULL
```

2. Käivita dbt testid uuesti:
```bash
docker compose exec dbt dbt test
docker compose exec dbt dbt docs generate
```

3. Käivita OpenMetadatas dbt ingestion pipeline uuesti (mine teenuse ingestion lehele ja vajuta **Run**)

4. Kontrolli, et uue testi tulemus on nähtav OpenMetadatas

### Aruteluks

- Miks on hea, et nii dbt kui OpenMetadata testid on nähtavad samas kohas?
- Kuidas seadistaksid teavitused andmekvaliteedi probleemide korral tootmiskeskkonnas?
- Millal eelistaksid OpenMetadata teste dbt testidele ja vastupidi?

---

## Keskkonna sulgemine

```bash
# Peata konteinerid
docker compose down

# Peata konteinerid JA kustuta andmed (andmebaasi sisu, OpenMetadata metaandmed, Elasticsearch indeks kaovad)
docker compose down -v
```
