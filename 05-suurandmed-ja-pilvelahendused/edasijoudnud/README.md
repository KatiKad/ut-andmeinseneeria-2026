# Praktikum 5: Suurandmed ja pilvelahendused (Edasijõudnud)

## Eesmärk

Teha Spark DataFrame põhiseid transformatsioone suurtel andmestikel ning mõista kaasaegsete andmejärvede (data lakehouse) tööpõhimõtet. Praktikumi lõpuks oskad põhjendada partitsioneerimise valikut ja tead, kus ja miks Delta Lake tüüpi lahendust praktikas kasutatakse.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Kirjutab Spark DataFrame transformatsioone (select, filter, withColumn, groupBy, agg, join, window)
- Võrdleb sama päringut DataFrame API-s ja Spark SQL-is ning selgitab, millal kumba eelistada
- Loeb ja kirjutab andmeid CSV, Parquet ja Delta formaatides ning mõõdab erinevust
- Põhjendab `partitionBy` valikut ja tõestab partition pruning töötamist `EXPLAIN` plaani abil
- Teeb Delta tabelile MERGE, UPDATE ja DELETE operatsioone ning kasutab time travel ajalooks
- Kirjeldab medaljoni arhitektuuri (bronze/silver/gold) mini-näite abil

## Eeldused

- Aktiivne Databricks Free Edition konto ([signup.databricks.com](https://signup.databricks.com)). Vana Community Edition on alates 01.01.2026 suletud.
- Töötav Python- ja SQL-kogemus eelmistest moodulitest.
- Läbitud baastaseme praktikum (Parquet, avatud tabeliformaadid, Databricksi sissejuhatus).

Databricks Free Edition tähendab praktiliselt:

- **Ainult serverless compute.** Klastreid ei looda. Esimene käivitus võib võtta 30-60 sekundit.
- **Päevane kvoodipiir.** Kui kvoot saab täis, lülitatakse compute päeva lõpuni välja. Ära jäta praktikumi viimasesse tundi.
- **Ühetasandiline workspace.** Üks konto, üks metastore, tabelid lähevad `main` kataloogi.
- **Väljaminev internetiühendus on piiratud.** Avalikud URL-id ei pruugi töötada. Kasutame eelkõige `samples` kataloogi ja Azure Open Datasets allikat.
- **JDBC/ODBC välist ligipääsu ei ole.** Kogu töö käib notebook'ides.

Piirangute kirjeldused: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations

## Andmed

Kasutame kahte andmekogumit:

1. **`samples.nyctaxi.trips`**: Databricksi sisseehitatud väike NYC taksosõitude näidis. Alati saadaval. Kasutame API õppimiseks ja sissejuhatavateks harjutusteks.
2. **NYC Yellow Taxi täismahus parquet**: 1.5 miljardit rida. Siin näeb "suurandmete" mõju: partitsioneerimise ja formaadi valik muudab päringu aega märgatavalt.

## Andmete ettevalmistus

Tee need sammud enne praktikumi algust. Iga samm on mõeldud tegemiseks Databricks notebook'i lahtris.

### Samm 1: kontrolli `samples` kataloogi saadavust

Loo uus notebook (Workspace → Create → Notebook). Esimene lahter:

```python
spark.sql("SELECT * FROM samples.nyctaxi.trips LIMIT 5").display()
```

Kui näed tabelit viie reaga, on kõik korras. Kui näed viga "Table not found", kontrolli, et workspace on seotud Unity Catalogiga (Free Edition'is peaks see vaikimisi nii olema).

### Samm 2: kontrolli NYC Taxi suurandmestiku ligipääsu

**Azure Open Datasets:**

```python
yellow_path = "wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/yellow"
df = spark.read.parquet(yellow_path)
print("Ridu:", df.count())
df.printSchema()
```

Täpsem info: https://learn.microsoft.com/en-us/azure/open-datasets/dataset-taxi-yellow?tabs=pyspark

## Praktikumi struktuur

Praktikum kestab 2 tundi. Läbi notebook'id järjestikku.

| Järk | Notebook | Aeg | Sisu |
|------|----------|-----|------|
| 1 | [01_spark_transformatsioonid.ipynb](./01_spark_transformatsioonid.ipynb) | ~30 min | DataFrame API põhiteisendused, joinid, window functions, SQL vs DataFrame API |
| 2 | [02_failiformaadid_ja_partitsioneerimine.ipynb](./02_failiformaadid_ja_partitsioneerimine.ipynb) | ~25 min | CSV / Parquet / Delta võrdlus päris andmetel, `partitionBy`, partition pruning EXPLAIN plaanist |
| 3 | [03_delta_lake_lakehouse.ipynb](./03_delta_lake_lakehouse.ipynb) | ~20 min | Delta ACID operatsioonid, time travel, medaljoni arhitektuur mini-näitel |

Kokku ~75 min notebook'ide osa + ~15-20 min platvormiteemad (vt allpool). "Proovi ise" ülesanded jäävad iseseisvaks tööks.

## Databricksi platvormi teemad (loeng)

Lisaks notebook'idele vaatame loengus läbi kolm Databricksi platvormi komponenti, millega andmeinsener iga päev kokku puutub. Arvesta ~15-20 min.

### SQL Warehouses

Serverless SQL arvutusmootor analüütikutele, kes eelistavad puhast SQL-i notebook'idele. Eraldab andmeinseneri (notebook + Spark) ja analüütiku (SQL Editor) töökoormused — ühed ressursid ei "võta teiselt ära".

Mida näeme: Workspace → SQL → SQL Editor → päring `samples.nyctaxi.trips` peale. Sama tulemus mis notebook'is, aga kasutajaliides on SQL-analüütikule optimeeritud.

Free Edition: saadaval, jagab päevast kvooti notebook compute'iga.

Viide: https://docs.databricks.com/en/compute/sql-warehouse/index.html

### Unity Catalog

Metaandmete halduse kiht kolmetasandilise nimistikuga `catalog.schema.table`. Enne Unity Catalogit oli iga workspace eraldiseisev. Unity Catalog annab:

- ühe kataloogi mitme workspace'i peale,
- ligipääsu tabeli- ja veerutasandil (`GRANT SELECT ON TABLE ...`),
- andmete pärinevuse (data lineage),
- Volumes — hallatud failihoidla tabelite kõrval (kasutame seda notebook 02-s).

Mida näeme: Catalog Explorer → `main` → `default` → olemasolevad tabelid ja notebook'is loodud `taxi_bronze` / `taxi_silver` / `taxi_gold_daily`.

Free Edition: üks metastore, üks catalog (`main`). Ligipääsuõiguste demot ei tee (ainult üks kasutaja).

Viide: https://docs.databricks.com/en/data-governance/unity-catalog/index.html

### Jobs / Workflows

Databricks Job on ajastatud või käsitsi käivitatav pipeline-samm — viis, kuidas notebook muutub tootmispipeline'iks ilma välise orkestreerijata (Airflow jms). Tüüpiline kasutus: iga hommikul kell 6 jookseb bronze → silver → gold.

Mida näeme: Workflows → Create Job → Task type: Notebook → Schedule (CRON). Jobid logivad automaatselt: käivitusaeg, kestus, õnnestumine / vead; saab siduda e-maili teavitusi ja aheldada mitu taski.

Free Edition: saadaval, jagab kvooti. Ära pane cron'i peale midagi tunnilist.

#### Koodinäide: gold tabeli uuendamine job'iga

See näide eeldab, et praktikumi 03 `taxi_silver` tabel on Unity Catalogis olemas. Loo uus notebook nimega `job_update_gold` sisuga:

```python
import pyspark.sql.functions as F
from datetime import datetime

print(f"Job käivitus: {datetime.now()}")

silver = spark.table("taxi_silver")

gold = (
    silver
    .withColumn("pickup_date", F.to_date("pickup_ts"))
    .groupBy("pickup_date")
    .agg(
        F.count("*").alias("trip_count"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.avg("total_amount"), 2).alias("avg_revenue_per_trip"),
    )
    .orderBy("pickup_date")
)

gold.write.mode("overwrite").format("delta").saveAsTable("taxi_gold_daily")

print(f"Gold tabel uuendatud: {spark.table('taxi_gold_daily').count()} rida")
spark.sql("DESCRIBE HISTORY taxi_gold_daily") \
     .select("version", "timestamp", "operation") \
     .show(5, truncate=False)
```

Seejärel Workflows → Create Job:

1. Nimi: `demo_daily_gold`
2. Task: vali `job_update_gold` notebook
3. Compute: Serverless (vaikimisi Free Edition'is)
4. Schedule: Manual (demoks), hiljem nt `0 6 * * *`
5. Create → Run now

Iga käivitus tekitab `taxi_gold_daily` tabelisse uue Delta versiooni (`DESCRIBE HISTORY` näitab). Nii saab ühest notebook'ist ühe klõpsuga ajastatud tootmistoru — mitme taski aheldamine katab lihtsamatel juhtudel ära Airflow-laadse orkestreerimise vajaduse.

Viide: https://docs.databricks.com/en/workflows/index.html


## Tulemus

Praktikumi lõpuks peaks osaleja suutma:

- Näidata vähemalt ühte enda kirjutatud DataFrame transformatsiooni ja selle SQL-ekvivalenti.
- Esitada `EXPLAIN` plaan, mis tõestab, et partitsioneeritud Parquet päring loeb ainult osa failidest.
- Näidata Delta tabelit, millel on vähemalt 3 versiooni (`DESCRIBE HISTORY`), ja tuua esile varasem versioon time travel'iga.
- Selgitada oma sõnadega, mis on medaljoni arhitektuur ja miks bronze-silver-gold kihid on eraldi.

## Veaotsing

### Sümptom: notebook'i käivitamine võtab kaua

**Diagnostikasammud.** Vaata notebook'i ülemise parema nurga status-indikaatorit. Kui kirjas on "Starting", on tegu serverless compute külmkäivitusega.

**Lahendus.** Oota 30-60 sekundit. Järgmised lahtrid käivituvad kiiremini. Väldi lahtrite ükshaaval ootamist. Käivita terve notebook Run All-iga, kui lahtrid on sõltuvusteta.


### Sümptom: "Table not found: main.default.xxx"

**Diagnostikasammud.** Kontrolli aktiivset kataloogi ja skeemi:
```sql
SELECT current_catalog(), current_schema();
```

**Lahendus.** Kas tabeli nimi on puudulik (ei sisalda `main.default.` prefiksit), või pole tabelit veel loodud. Notebook'id loovad endale vajaminevad tabelid ise. Jooksuta lahtrid järjekorras algusest.

### Sümptom: "Serverless compute quota exceeded"

**Diagnostikasammud.** Vaata workspace'i "Compute" vahelehte. Kui seal on kirjas "Quota exceeded", on päevane kvoot täis.

**Lahendus.** Tänaseks kõik, jätka homme :-). Kvoot uueneb iga päev.

### Sümptom: `%fs ls` või `dbutils.fs.ls` annab permission denied

**Diagnostikasammud.** Free Edition'is on failisüsteemi ligipääs piiratud. Kontrolli, et proovid Volumes teed (`/Volumes/main/default/...`) või Delta tabeli asukohta (`DESCRIBE EXTENDED <tabel>`).

**Lahendus.** Kasuta `SHOW TABLES` või Catalog Explorerit. Otse DBFS juurkataloogi ei saa enam uurida. Partition-kausta uurimiseks kasuta tabeli nime ja `DESCRIBE DETAIL`.

## FAQ

**K: Miks ei kasuta me klastreid nagu vanas Community Edition?**
V: Databricks Free Edition (alates 01.01.2026) kasutab ainult serverless compute'i. Klastrite loomist ei ole ja seda ei ole vaja. Spark käivitub automaatselt esimese lahtri käivitamisel.

**K: Miks me ei loo `SparkSession`-i käsitsi?**
V: Databricksi notebook'is on muutuja `spark` juba olemas. Ära kirjuta `SparkSession.builder.getOrCreate()`. See on ainult väljaspool Databricksi vajalik.

**K: Kas saan notebook'e kohalikus masinas jooksutada?**
V: Teoreetiliselt jah, aga praktikum on kirjutatud Databricks Free Edition'i jaoks. Kohaliku PySpark'i puhul kaob ära `samples` kataloog, Unity Catalog tabelite sõnastus ja osa Delta integratsiooni. Kui tahad siiski lokaalselt jooksutada, võid kasutada nt sellist Docker image-t: https://quay.io/repository/jupyter/pyspark-notebook  
NB arvesta, et kood ei toimi üks ühele, kuna siin praktikumis kasutame osa funktsionaalsust mis on saadaval vaid Databricksis ja mitte vabavaralises Apache Sparkis. 
