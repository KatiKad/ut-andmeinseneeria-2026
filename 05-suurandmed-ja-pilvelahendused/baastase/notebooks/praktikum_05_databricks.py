# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Praktikum 5: Databricksi praktiline osa
# MAGIC
# MAGIC See notebook sisaldab baastaseme praktikumi praktilist töökäiku.
# MAGIC
# MAGIC Siin teed läbi järgmised sammud:
# MAGIC - valid oma workspace catalogi;
# MAGIC - lood skeemi `praktikum_05`;
# MAGIC - loed sample-andmed tabelist `samples.nyctaxi.trips`;
# MAGIC - teed lihtsa `PySpark` teisenduse;
# MAGIC - salvestad tulemuse oma `Delta` tabelisse;
# MAGIC - kontrollid, et tabel loodi õigesti.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Enne alustamist
# MAGIC
# MAGIC Veendu, et notebook on ühendatud serverless compute'iga.
# MAGIC
# MAGIC Kui see notebook on Databricksi imporditud lähtefailina, siis:
# MAGIC - iga allolev plokk on eraldi lahter;
# MAGIC - käivita lahtrid ülevalt alla;
# MAGIC - kui mõni lahter annab vea, lahenda see enne järgmise käivitamist.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Vaata, millised catalogid sul on
# MAGIC
# MAGIC Selles sammus vaatad üle, millised catalogid on sulle nähtavad.
# MAGIC
# MAGIC Otsi tulemuste hulgast:
# MAGIC - `samples` catalogit, kust loeme näidisandmeid;
# MAGIC - oma workspace catalogit, kuhu saad luua skeemi ja tabeli.

# COMMAND ----------
# Käivitame SQL käsu, mis loetleb kõik sulle nähtavad catalogid.
# `display(...)` näitab tulemuse mugava tabelina notebooki väljundis.
display(spark.sql("SHOW CATALOGS"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Loo skeem `praktikum_05`
# MAGIC
# MAGIC Kirjuta järgmises lahtris oma workspace catalogi nimi.
# MAGIC
# MAGIC Ära kasuta siin `samples` catalogit.

# COMMAND ----------
# Kirjuta siia oma workspace catalogi nimi.
workspace_catalog = "<kirjuta siia oma workspace catalogi nimi>"

# Selle praktikumi skeemi nimi.
workspace_schema = "praktikum_05"

# Koostame catalogi ja skeemi SQL-kujud eraldi muutujatesse.
# Nii on allpool päringuid lihtsam lugeda.
catalog_identifier = f"`{workspace_catalog}`"
schema_identifier = f"`{workspace_schema}`"

# CREATE SCHEMA IF NOT EXISTS tähendab:
# kui skeem on juba olemas, siis viga ei anta ja sama töö võib rahulikult jätkuda.
create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {catalog_identifier}.{schema_identifier}"

spark.sql(create_schema_sql)

# Näita kontrolliks, millised skeemid selles catalogis olemas on.
show_schemas_sql = f"SHOW SCHEMAS IN {catalog_identifier}"
display(spark.sql(show_schemas_sql))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Ava sample-andmed
# MAGIC
# MAGIC Loeme sisse Databricksi sample-tabeli `samples.nyctaxi.trips`.
# MAGIC
# MAGIC Vaata üle, et andmetes oleksid olemas vähemalt veerud:
# MAGIC - `pickup_zip`
# MAGIC - `trip_distance`
# MAGIC - `fare_amount`

# COMMAND ----------
# Loeme olemasoleva sample-tabeli Spark DataFrame'iks.
# DataFrame on Sparkis tabelilaadne andmestruktuur, mille peal saame edasi töötada.
trips = spark.read.table("samples.nyctaxi.trips")

# `limit(20)` võtab ainult väikese eelvaate.
# Nii näed andmete kuju enne, kui hakkad neid töötlema.
display(trips.limit(20))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Tee teisendus
# MAGIC
# MAGIC Selles sammus:
# MAGIC - jätad alles vajalikud veerud;
# MAGIC - filtreerid välja read, mida ei taha kasutada;
# MAGIC - lood veeru `distance_band`;
# MAGIC - rühmitad read `pickup_zip` ja `distance_band` järgi;
# MAGIC - arvutad mõõdikud.
# MAGIC
# MAGIC Selle tabeli granulaarsus on:
# MAGIC
# MAGIC `üks rida ühe pickup_zip ja distance_band kombinatsiooni kohta`
# MAGIC
# MAGIC Iga rida kirjeldab üht pealevõtu postiindeksi ja sõidupikkuse vahemiku kombinatsiooni.
# MAGIC
# MAGIC Mõõdikud on:
# MAGIC - `trip_count`
# MAGIC - `avg_trip_distance`
# MAGIC - `avg_fare_amount`

# COMMAND ----------
# Impordime Spark SQL funktsioonid lühinimega `F`.
# See on PySparkis levinud töövõte, et funktsioonikutsed jääksid lühemad ja loetavamad.
from pyspark.sql import functions as F

summary = (
    trips
    # Jätame alles ainult need veerud, mida selles praktikumis päriselt kasutame.
    .select("pickup_zip", "trip_distance", "fare_amount")
    # Filtreerime välja read, kus pealevõtu postiindeks puudub.
    .where("pickup_zip IS NOT NULL")
    # Filtreerime välja read, kus sõidupikkus ei ole sisukas.
    .where("trip_distance > 0")
    # Filtreerime välja read, kus hind ei ole sisukas.
    .where("fare_amount > 0")
    # Loome uue kirjeldava tunnuse `distance_band`.
    # See jagab sõidud lihtsatesse pikkusvahemikesse.
    .withColumn(
        "distance_band",
        # F.when(...).otherwise(...) töötab nagu tingimuslause.
        F.when(F.col("trip_distance") < 2, "0-2 mi")
         .when(F.col("trip_distance") < 5, "2-5 mi")
         .otherwise("5+ mi")
    )
    # Rühmitame read kahe tunnuse järgi.
    # Granulaarsus muutub siin kujule:
    # üks rida ühe pickup_zip ja distance_band kombinatsiooni kohta.
    .groupBy("pickup_zip", "distance_band")
    # Arvutame iga rühma kohta mõõdikud.
    .agg(
        # Loeme, mitu sõitu sellesse rühma kuulub.
        F.count("*").alias("trip_count"),
        # Arvutame keskmise sõidupikkuse ja ümardame kahe komakohani.
        F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
        # Arvutame keskmise hinna ja ümardame kahe komakohani.
        F.round(F.avg("fare_amount"), 2).alias("avg_fare_amount")
    )
    # Sorteerime tulemuse nii, et sama pickup_zip väärtuse read oleksid koos.
    .orderBy("pickup_zip", "distance_band")
)

# Kuvame saadud kokkuvõtte tabelina.
display(summary)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Vaata kõige suurema sõitude arvuga ridu
# MAGIC
# MAGIC Eelmise lahtri tulemus võib olla pikk.
# MAGIC
# MAGIC See lahter aitab vaadata kõige aktiivsemaid kombinatsioone.

# COMMAND ----------
# Sorteerime read kõige suurema sõitude arvu järgi kahanevalt
# ja näitame ainult 30 esimest rida.
display(summary.orderBy(F.desc("trip_count")).limit(30))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Salvesta tulemus oma tabelisse
# MAGIC
# MAGIC Databricks loob sellest kirjutusest vaikimisi `Delta Lake` tabeli.
# MAGIC
# MAGIC Tabeli nimi tekib kujul:
# MAGIC
# MAGIC `catalog.schema.user_<kasutaja>_taxi_trip_summary`

# COMMAND ----------
# session_user() tagastab aktiivse kasutaja nime.
# regexp_replace(...) asendab sobimatud märgid alakriipsuga,
# et tabelinimi oleks turvaline ja loetav.
username_safe = spark.sql(
    "SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_') AS username"
).first()["username"]

# Tabeli enda nimi ilma catalogi ja skeemita.
target_table_name = f"user_{username_safe}_taxi_trip_summary"

# Koostame täieliku SQL-identifikaatori kujul catalog.schema.table.
# Iga osa on eraldi backtickides, et erimärgid ei tekitaks viga.
target_table_identifier = f"{catalog_identifier}.{schema_identifier}.`{target_table_name}`"

# write.mode("overwrite") tähendab:
# kui sama tabel on juba olemas, kirjutatakse see uue sisuga üle.
# saveAsTable(...) salvestab DataFrame'i Databricksis tabelina.
summary.write.mode("overwrite").saveAsTable(target_table_identifier)

# Prindime välja loodud tabeli nime, et seda oleks järgmistes sammudes lihtne kasutada.
print(f"Loodi tabel: {target_table_identifier}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Kontrolli tulemust
# MAGIC
# MAGIC Loe loodud tabel tagasi sisse ja vaata, kas andmed on olemas.

# COMMAND ----------
# Loeme äsja loodud tabeli SQL päringuga tagasi sisse.
# Nii kontrollid, et salvestus päriselt õnnestus.
select_target_table_sql = f"SELECT * FROM {target_table_identifier} ORDER BY trip_count DESC LIMIT 30"

display(spark.sql(select_target_table_sql))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Tee nähtavaks, et tabel on `Delta`
# MAGIC
# MAGIC `DESCRIBE DETAIL` näitab tabeli tehnilisi omadusi.
# MAGIC
# MAGIC Otsi väljundist veergu `format`.
# MAGIC Kui selle väärtus on `delta`, siis on tabel loodud `Delta Lake` formaadis.

# COMMAND ----------
# DESCRIBE DETAIL näitab tabeli tehnilisi omadusi.
# Siit saad kinnituse, et tegemist on Delta tabeliga.
describe_target_table_sql = f"DESCRIBE DETAIL {target_table_identifier}"
display(spark.sql(describe_target_table_sql))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Soovi korral: andmekvaliteedi kiire kontroll
# MAGIC
# MAGIC See lahter ei ole kohustuslik, aga aitab mõelda, kas tulemus tundub usaldusväärne.
# MAGIC
# MAGIC Kontrolli näiteks:
# MAGIC - kas `trip_count` on alati positiivne;
# MAGIC - kas mõõdikud ei ole `NULL`;
# MAGIC - kas sama `pickup_zip` ja `distance_band` kombinatsioon ei kordu.

# COMMAND ----------
# See päring teeb mõned lihtsad kvaliteedikontrollid ühe kokkuvõttereaga.
# Eesmärk ei ole täielik testpakett, vaid esimene kiire kontroll.
quality_check_sql = f"""
SELECT
  -- Mitu rida kokku tabelis on.
  COUNT(*) AS row_count,
  -- Mitu rida sisaldab mittesobivat trip_count väärtust.
  SUM(CASE WHEN trip_count <= 0 THEN 1 ELSE 0 END) AS non_positive_trip_count_rows,
  -- Mitu rida sisaldab puuduvat keskmist sõidupikkust.
  SUM(CASE WHEN avg_trip_distance IS NULL THEN 1 ELSE 0 END) AS null_distance_rows,
  -- Mitu rida sisaldab puuduvat keskmist hinda.
  SUM(CASE WHEN avg_fare_amount IS NULL THEN 1 ELSE 0 END) AS null_fare_rows
FROM {target_table_identifier}
"""

quality_check = spark.sql(quality_check_sql)

# Kuvame kvaliteedikontrolli tulemuse tabelina.
display(quality_check)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 10. Soovi korral: käivita notebook job'ina
# MAGIC
# MAGIC Seda sammu ei tehta selles notebookis koodiga, vaid Databricksi kasutajaliideses.
# MAGIC
# MAGIC Lühike töövoog:
# MAGIC 1. ava notebooki ülaribal `Schedule`;
# MAGIC 2. loo notebooki jaoks job;
# MAGIC 3. käivita `Run now`;
# MAGIC 4. kontrolli run-i tulemust.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 11. Soovi korral: koristamine
# MAGIC
# MAGIC Kui tahad praktikumi hiljem puhtalt uuesti teha, saad skeemi kustutada.
# MAGIC
# MAGIC Ära käivita järgmist lahtrit kohe, kui tahad tabelit alles hoida.

# COMMAND ----------
# Kui tahad skeemi kustutada, eemalda järgmiselt realt kommentaarimärk.
# See kustutab skeemi koos selle sees olevate tabelitega.
# drop_schema_sql = f"DROP SCHEMA IF EXISTS {catalog_identifier}.{schema_identifier} CASCADE"
# spark.sql(
#     drop_schema_sql
# )
