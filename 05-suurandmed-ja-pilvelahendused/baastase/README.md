# Praktikum 5: Suurandmed ja pilvelahendused (Baastase)

## Sisukord

- [Praktikumi eesmärk](#praktikumi-eesmärk)
- [Õpiväljundid](#õpiväljundid)
- [Hinnanguline ajakulu](#hinnanguline-ajakulu)
- [Eeldused](#eeldused)
- [Enne alustamist](#enne-alustamist)
- [Praktikumi failid](#praktikumi-failid)
- [Kuidas notebooki lahtrid töötavad?](#kuidas-notebooki-lahtrid-tootavad)
- [Kus see praktikum toimub?](#kus-see-praktikum-toimub)
- [Miks see teema on oluline?](#miks-see-teema-on-oluline)
- [Uued mõisted](#uued-mõisted)
- [Soovitatud töötee](#soovitatud-töötee)
- [1. Ava Databricks ja loo uus notebook](#1-ava-databricks-ja-loo-uus-notebook)
- [2. Ühenda notebook serverless compute'iga](#2-ühenda-notebook-serverless-computeiga)
- [3. Vaata, millised catalogid sul on](#3-vaata-millised-catalogid-sul-on)
- [4. Loo skeem `praktikum_05`](#4-loo-skeem-praktikum_05)
- [5. Ava sample-andmed](#5-ava-sample-andmed)
- [6. Tee lihtne PySpark teisendus](#6-tee-lihtne-pyspark-teisendus)
- [7. Salvesta tulemus oma tabelisse](#7-salvesta-tulemus-oma-tabelisse)
- [8. Kontrolli tulemust notebookis ja Catalog vaates](#8-kontrolli-tulemust-notebookis-ja-catalog-vaates)
- [9. Käivita sama notebook job'ina](#9-käivita-sama-notebook-jobina)
- [10. Seo nähtud töö ETL-iga](#10-seo-nähtud-töö-etliga)
- [Kontrollpunktid](#kontrollpunktid)
- [Levinud vead ja lahendused](#levinud-vead-ja-lahendused)
- [Kokkuvõte](#kokkuvõte)
- [Valikulised lisaülesanded](#valikulised-lisaulesanded)
- [Koristamine](#koristamine)
- [Kasutatud allikad](#kasutatud-allikad)

## Praktikumi eesmärk

Selle praktikumi eesmärk on teha läbi esimene väike andmetöötluse töövoog Databricks Free Editionis.

Praktikumi lõpuks oskad:

- avada ja kasutada `Python` notebooki Databricksi veebikeskkonnas;
- lugeda Databricksi näidisandmeid tabelist `samples.nyctaxi.trips`;
- teha lihtsa `PySpark` teisenduse;
- salvestada tulemuse oma tabelisse eraldi skeemis;
- käivitada sama notebooki job'ina.

Selle praktikumi teine eesmärk on siduda nähtud sammud suurandmete põhimõistetega. Näed, kuidas `Parquet`, `Delta Lake`, hajussüsteem ja pilvekeskkond päris tööriistas kokku saavad.

## Õpiväljundid

Praktikumi lõpuks oskad:

- selgitada, miks kasutatakse analüütikas `Parquet` formaati;
- kirjeldada oma sõnadega, mida teeb avatud tabeliformaat nagu `Delta Lake`;
- selgitada, mida tähendab hajussüsteem;
- kasutada Databricks Free Editioni baastasemel;
- luua oma workspace catalogi alla skeemi `praktikum_05`;
- lugeda tabelit `PySpark` abil, teha sellele lihtsa teisenduse ja salvestada tulemus uue tabelina;
- kontrollida, et loodud tabel on `Delta` formaadis;
- käivitada notebooki käsitsi job'ina.

## Hinnanguline ajakulu

Arvesta umbes 90 kuni 120 minutiga.

See aeg jaguneb ligikaudu nii:

- 15 min keskkonna ja tööruumiga tutvumiseks;
- 15 min sample-andmete vaatamiseks;
- 25 min esimese teisenduse tegemiseks;
- 15 min tabeli salvestamiseks ja kontrollimiseks;
- 15 min job'i loomise ja käivituse proovimiseks;
- 10 kuni 35 min kokkuvõtteks ja lisaosa proovimiseks.

## Eeldused

Sul on vaja:

- Databricks Free Edition kontot;
- ligipääsu Databricksi tööruumi veebiliidesele;
- veebibrauserit;
- põhiteadmisi `Python`-ist ja `SQL`-ist;
- eelmiste praktikumide põhjal üldist arusaama, mis on tabel, päring ja andmete töötlemine.

Selle praktikumi jaoks ei ole vaja:

- Dockerit;
- kohalikku andmebaasi;
- `VS Code` terminali;
- oma arvutisse paigaldatud `Spark`-i.

Kui sul ei ole veel Free Edition kontot, loo see enne praktikumi algust Databricksi ametliku Free Editioni lehe kaudu.

## Enne alustamist

### Valmisoleku kontroll

Enne praktikumi kontrolli üle järgmised asjad:

- saad Databricksi tööruumi sisse logida;
- vasakus menüüs on näha vähemalt `Workspace` ja `Catalog`;
- sul on võimalik luua uus notebook;
- notebooki saab ühendada serverless compute'iga;
- mõistad, et selles praktikumis kasutame ainult `Python` notebooki.

### Mida täna ei tee

Selles praktikumis me ei tee järgmisi asju:

- ei kasuta `Scala` ega `R` notebooke;
- ei seadista klastri tüüpi compute'i;
- ei lae andmeid internetist notebooki koodiga alla;
- ei kasuta `DBFS mount` lahendust;
- ei tee jõudluse analüüsi Spark UI põhjal.

Need piirangud ei ole juhuslikud. Databricks Free Edition on teadlikult lihtsustatud keskkond. Baastaseme jaoks on see hea, sest saame keskenduda ühele selgele töövoole.

## Praktikumi failid

Selles praktikumis ei kasuta sa eraldi kohalikke andmefaile ega skripte.

Praktikumi põhirada ise toimub Databricksi veebiliideses. Kohalikust repositooriumist ei ole vaja ühtegi andmefaili Databricksi üles laadida.

Selles kaustas on sulle oluline eelkõige see juhend:

- [`README.md`](./README.md)
- [`notebooks/praktikum_05_databricks.py`](./notebooks/praktikum_05_databricks.py) on Databricksi notebooki lähtefail praktilise osa jaoks

Kui tahad praktilise osa Databricksi valmis notebookina üles laadida, kasuta faili [`notebooks/praktikum_05_databricks.py`](./notebooks/praktikum_05_databricks.py).

See fail on Databricksi source-formaadis notebook. Selle saad Databricksi tööruumi importida `Workspace` vaates valikuga `Import` või lihtsalt faili tööruumi lohistades.

## Kuidas notebooki lahtrid töötavad?

Databricksi notebook koosneb lahtritest. Inglise keeles kasutatakse sageli sõna `cell`.

Iga lahter on üks eraldi käivitatav plokk. Tavaliselt on ühes lahtris üks loogiline samm.

Selles juhendis kehtib lihtne reegel:

- iga allpool toodud koodiplokk käib ühte eraldi lahtrisse;
- kleebi kogu koodiplokk korraga samasse lahtrisse;
- käivita lahter klahvidega `Shift+Enter` või nupuga `Run cell`.

`Shift+Enter` teeb korraga kaks asja:

- käivitab praeguse lahtri;
- liigub järgmisse lahtrisse või loob vajadusel uue.

Kui mõni lahter annab vea, siis peatu ja lahenda see enne järgmise lahtri käivitamist. Notebookis sõltuvad hilisemad sammud sageli sellest, et varasemad muutujad, näiteks `trips`, `summary` või `target_table_identifier`, oleksid juba loodud.

## Kus see praktikum toimub?

See praktikum toimub peaaegu täielikult Databricksi veebiliideses.

Oluline on mitte ajada segi kolme eri keskkonda:

- see repositoorium sinu arvutis või Codespace'is;
- Databricksi veebitööruum brauseris;
- Databricksi serverless compute, mille peal notebooki kood päriselt jookseb.

Selles praktikumis teed kõik põhisammud Databricksi veebiliideses.

Kui mõnes varasemas praktikumis kasutasid terminali, `psql`-i või `docker compose` käske, siis täna neid vaja ei ole.

## Miks see teema on oluline?

Kui andmemaht kasvab, ei piisa alati sellest, et loed ühe `CSV` faili oma arvutisse ja töötled seda ühes protsessis.

Praktikas tekivad kiiresti kolm probleemi:

1. andmeid on palju;
2. päringud peavad olema kiired;
3. töö peab olema korduv ja hallatav.

`Parquet` aitab vähendada lugemise mahtu. Veerupõhine vorming sobib hästi analüütikaks, sest sa ei pea iga kord kogu rida sisse lugema.

Avatud tabeliformaat, näiteks `Delta Lake`, lahendab järgmise probleemi. Ainult failidest ei piisa alati, sest vaja on ka usaldusväärset tabeliloogikat, skeemi muutmist ja korduvat kirjutamist.

Hajussüsteem lahendab kolmanda probleemi. Kui töö ja andmed jaotatakse mitme masina vahel, ei pea kogu töö käima ühe arvuti peal.

Databricks toob need ideed kokku. Sul on veebikeskkond, kus saad andmeid lugeda, töödelda, tabelina salvestada ja sama töö hiljem uuesti käivitada.

## Uued mõisted

### Miks `CSV`-st alati ei piisa?

`CSV` on lihtne ja mugav vahetusformaat.

Probleem on selles, et `CSV` ei ole suurte analüütiliste tööde jaoks eriti tõhus. Seal ei ole tüüpe, veerupõhist salvestust ega tabeli ajalugu.

Kui sul on vaja kiiremaid päringuid ja töökindlamat tabelikihti, on vaja midagi enamat.

### `Parquet`

`Parquet` on veerupõhine failivorming.

See lahendab probleemi, kus analüütiline päring vajab ainult mõnda veergu, aga reaformaadis fail sunniks kogu rea sisse lugema.

Näide:

Kui tabelis on 30 veergu, aga sinu päring vajab ainult kahte, siis `Parquet` aitab lugeda vähem andmeid.

Tehniline detail:

`Parquet` salvestab andmeid veergude kaupa. See sobib hästi analüütiliste päringute ja tihendamise jaoks.

### Avatud tabeliformaat

Failivormingust üksi ei piisa, kui tahad tabelit usaldusväärselt uuendada.

Avatud tabeliformaat lisab failidele tabeli käitumise. See tähendab näiteks skeemi haldust, kirjutuste jälgimist ja paremat korduvust.

Selles praktikumis puutud kõige otsesemalt kokku formaadiga `Delta Lake`.

Databricksi puhul tähendab see tavaliselt, et tabeli taga on `Parquet` failid ja lisaks logi, mis kirjeldab tabeli muutusi.

Oluline täpsustus selle praktikumi kohta:

Selles juhendis sa ei loo eraldi `.parquet` faili ega ava seda käsitsi. Selle asemel lood Databricksis `Delta` tabeli. `Parquet` on siin allkiht, mida `Delta Lake` kasutab.

### Hajussüsteem

Hajussüsteem on süsteem, kus töö ja andmed on jaotatud mitme masina vahel.

See lahendab probleemi, kus üks arvuti jääb töömahu või andmemahu jaoks kitsaks.

Näide:

Kui tahad töödelda miljonite või miljardite ridadega andmeid, on mõistlik jagada töö väiksemateks osadeks.

`Spark` ongi üks selline tööriist. Databricks kasutab `Spark`-i hajustöötluse mootorina.

### `Unity Catalog`

Kui sul on palju tabeleid, on vaja neid kusagil hallata.

`Unity Catalog` on Databricksi ühtne metaandmete ja õiguste kiht. Seal elavad catalogid, skeemid ja tabelid.

Selles praktikumis näed vähemalt kahte olulist nime:

- `samples` on Databricksi näidisandmete catalog;
- sinu enda tabel läheb sinu workspace catalogi skeemi `praktikum_05`.

### Serverless compute

Ka andmetöötlus vajab arvutusressurssi.

Serverless compute tähendab siin seda, et sa ei pea ise masinat või klastrit käsitsi seadistama. Databricks annab sulle vajaliku arvutusressursi automaatselt.

Baastaseme jaoks on see hea, sest sa saad keskenduda töö sisule, mitte infrastruktuurile.

### Notebook

Notebook on töövihik, kus tekst, kood ja väljund on samas kohas.

See lahendab probleemi, kus õppija tahab näha sammu, koodi ja tulemust koos.

Selles praktikumis kasutad notebooki kahel moel:

- õpid seal andmeid uurima;
- käivitad sama notebooki hiljem job'ina.

## Soovitatud töötee

Soovitatud töötee on järgmine:

1. loo `Python` notebook;
2. ühenda see serverless compute'iga;
3. vaata üle oma catalogid;
4. loo selle praktikumi jaoks skeem `praktikum_05`;
5. loe sample-tabel `samples.nyctaxi.trips`;
6. tee sellele väike `PySpark` teisendus;
7. kuva tulemus ja tee üks lihtne visualiseering;
8. salvesta tulemus oma tabelisse;
9. käivita sama notebook job'ina.

See töötee aitab sul liikuda ühe uue oskuse kaupa. Kõigepealt harjud notebooki ja sample-andmetega. Seejärel teed lihtsa teisenduse ja salvestad tulemuse tabelina.

## 1. Ava Databricks ja loo uus notebook

See samm tehakse Databricksi veebiliideses.

1. Ava oma Databricksi Free Edition tööruum.
2. Vali vasakult menüüst `Workspace`.
3. Vali `New`, siis `Notebook`.
4. Pane notebookile nimi, näiteks `praktikum5_taxi_summary`.
5. Kontrolli, et notebooki keel oleks `Python`.

Miks see samm on oluline?

Notebook on tänase praktikumi põhikeskkond. Kõik järgmised sammud toimuvad siin.

Õnnestumise märk:

- uus notebook avaneb;
- esimene lahter on tühi;
- keeleks on märgitud `Python`.

Kui notebook avaneb mõnes muus keeles, vaheta see enne edasi liikumist `Python`-iks.

## 2. Ühenda notebook serverless compute'iga

See samm tehakse Databricksi veebiliideses.

Notebooki kood ei jookse lihtsalt brauseris. Selleks on vaja arvutusressurssi.

1. Vaata notebooki ülariba paremat poolt.
2. Kui notebook ei ole ühendatud, vali `Connect`.
3. Vali pakutud serverless compute'i variant.
4. Oota, kuni olek näitab, et notebook on ühendatud.

Mida see samm teeb?

See ühendab sinu notebooki Databricksi arvutuskeskkonnaga. Alles siis saab `Spark` koodi käivitada.

Õnnestumise märk:

- notebooki ülaribal on näha, et see on ühendatud;
- saad käivitada lihtsa testlahtri.

Proovi kohe väikest kontrolli:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# print(...) on tavaline Pythoni funktsioon.
# See kirjutab teksti väljundisse.
print("Notebook on valmis.")
```

Kui näed väljundis teksti `Notebook on valmis.`, siis ühendus töötab.

## 3. Vaata, millised catalogid sul on

See samm tehakse notebooki `Python` lahtris.

Enne andmete lugemist on kasulik aru saada, kust tabelid tulevad ja kuhu sinu enda tabel läheb.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# spark.sql(...) käivitab Databricksis SQL käsu.
# SHOW CATALOGS näitab, millised catalogid on sulle nähtavad.
# display(...) kuvab tulemuse tabelina notebooki väljundis.
display(spark.sql("SHOW CATALOGS"))
```

Mida see teeb?

See näitab sulle cataloge, mis sinu tööruumis olemas on.

Mida väljundist otsida?

- `samples` catalogit, kust loeme Databricksi näidisandmeid;
- oma workspace catalogit, kuhu saad hiljem ise tabeli kirjutada.

Pane oma workspace catalogi nimi kirja. Ära vali selleks `samples`, sest see on näidisandmete jaoks ja sinna me oma tabelit ei salvesta.

Kui väljundis on mitu nime ja sa ei ole kindel, milline neist on sinu workspace catalog, ava vasakult ka `Catalog` vaade. Seal on tavaliselt lihtsam näha, milline catalog kuulub sinu tööruumi.

## 4. Loo skeem `praktikum_05`

See samm tehakse notebooki `Python` lahtris.

Enne kui lood oma tabeli, tee selle praktikumi jaoks eraldi skeem.

See aitab kahte asja:

- praktikumi tabelid ei lähe segamini teiste katsetustega;
- hiljem on lihtsam kogu praktikumi sisu ühe käsuga ära koristada.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# Kirjuta siia oma workspace catalogi nimi.
# Selle leidsid eelmises sammus.
workspace_catalog = "<kirjuta siia oma workspace catalogi nimi>"

# Selle praktikumi skeemi nimi.
workspace_schema = "praktikum_05"

# Koostame catalogi ja skeemi SQL-kujud eraldi muutujatesse.
# Nii jäävad päringud loetavamaks ja Databricksi lint oskab neid paremini tõlgendada.
catalog_identifier = f"`{workspace_catalog}`"
schema_identifier = f"`{workspace_schema}`"

# CREATE SCHEMA IF NOT EXISTS loob skeemi ainult siis,
# kui seda veel olemas ei ole.
create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {catalog_identifier}.{schema_identifier}"
spark.sql(create_schema_sql)

# SHOW SCHEMAS näitab, millised skeemid selles catalogis olemas on.
show_schemas_sql = f"SHOW SCHEMAS IN {catalog_identifier}"
display(spark.sql(show_schemas_sql))
```

Mida see teeb?

- salvestab sinu workspace catalogi nime muutujasse `workspace_catalog`;
- määrab praktikumi skeemi nimeks `praktikum_05`;
- loob SQL-identifikaatorid muutujates `catalog_identifier` ja `schema_identifier`;
- loob selle skeemi, kui seda veel ei ole;
- näitab skeemide loendit, et saaksid tulemust kontrollida.

Miks me koostame SQL laused eraldi muutujates?

Databricksi `Python` lint võib mõnikord näidata eksitavat süntaksiviga mustri `spark.sql(f"...")` juures, kuigi kood ise töötab. Kui hoiad SQL lause esmalt eraldi muutujas ja alles siis annad selle funktsioonile `spark.sql(...)`, jääb kood õppija jaoks selgemaks.

Õnnestumise märk:

- väljundis näed skeemi `praktikum_05`;
- veateadet ei tule.

Kui saad õiguste vea, kontrolli, et kasutasid oma workspace catalogi nime, mitte `samples` catalogit.

## 5. Ava sample-andmed

See samm tehakse notebooki `Python` lahtris.

Selles praktikumis ei lae me andmeid ise üles. Kasutame valmis sample-tabelit `samples.nyctaxi.trips`.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# spark.read.table(...) loeb olemasoleva tabeli Spark DataFrame'iks.
trips = spark.read.table("samples.nyctaxi.trips")

# limit(20) võtab eelvaate jaoks esimesed 20 rida.
# display(...) näitab tulemuse tabelina.
display(trips.limit(20))
```

Mida see teeb?

- esimene rida loeb sample-tabeli `Spark DataFrame`-i;
- teine rida näitab esimest 20 rida.

Õnnestumise märk:

- näed tabelit;
- veergude seas on vähemalt `pickup_zip`, `trip_distance` ja `fare_amount`.

Kui tabel avaneb, on sul olemas tänase praktikumi `extract` ehk andmete sisse lugemise osa.

## 6. Tee lihtne PySpark teisendus

See samm tehakse notebooki `Python` lahtris.

Nüüd teed väikese töötluse. See on tänase praktikumi `transform` osa.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# Impordime Spark SQL funktsioonid lühinimega F,
# et saaksime neid allpool mugavamalt kasutada.
from pyspark.sql import functions as F

summary = (
    trips
    # select(...) jätab alles ainult vajalikud veerud.
    .select("pickup_zip", "trip_distance", "fare_amount")
    # where(...) filtreerib välja read, mida me ei taha kasutada.
    .where("pickup_zip IS NOT NULL")
    .where("trip_distance > 0")
    .where("fare_amount > 0")
    # withColumn(...) lisab uue veeru nimega distance_band.
    .withColumn(
        "distance_band",
        # F.when(...).otherwise(...) töötab nagu tingimuslause.
        F.when(F.col("trip_distance") < 2, "0-2 mi")
         .when(F.col("trip_distance") < 5, "2-5 mi")
         .otherwise("5+ mi")
    )
    # groupBy(...) koondab read rühmadesse.
    .groupBy("pickup_zip", "distance_band")
    # agg(...) arvutab iga rühma kohta kokkuvõtlikud näitajad.
    .agg(
        # F.count("*") loeb ridade arvu.
        F.count("*").alias("trip_count"),
        # F.avg("trip_distance") arvutab keskmise sõidupikkuse.
        F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
        # F.avg(...) arvutab keskmise ja F.round(..., 2) ümardab kahe komakohani.
        F.round(F.avg("fare_amount"), 2).alias("avg_fare_amount")
    )
    # orderBy(...) sorteerib tulemuse.
    .orderBy("pickup_zip", "distance_band")
)

# display(...) näitab saadud kokkuvõtet tabelina.
display(summary)
```

Mida see teeb?

- võtab algtabelist ainult vajalikud veerud;
- eemaldab read, kus vahemaa või hind ei sobi;
- loob uue veeru `distance_band`;
- rühmitab read `pickup_zip` ja `distance_band` kombinatsiooni järgi;
- arvutab iga kombinatsiooni kohta sõitude arvu, keskmise sõidupikkuse ja keskmise hinna.

See on hea esimene näide, sest siin on näha kolm olulist töövõtet:

- veergude valik;
- filtreerimine;
- rühmitamine ja agregeerimine.

Õnnestumise märk:

- näed väikest kokkuvõttetabelit;
- seal on veerud `pickup_zip`, `distance_band`, `trip_count`, `avg_trip_distance` ja `avg_fare_amount`.

### Seos dimensionaalse modelleerimisega

Kuigi selles praktikumis me eraldi dimensioonitabeleid ei loo, tasub lõpptabeli granulaarsus enne salvestamist selgelt sõnastada.

Selle tabeli granulaarsus on:

`üks rida ühe pickup_zip ja distance_band kombinatsiooni kohta`

See tähendab, et iga rida kirjeldab üht pealevõtu postiindeksi ja sõidupikkuse vahemiku kombinatsiooni ning selle kohta arvutatud mõõdikuid.

Selles näites on mõõdikud:

- `trip_count`;
- `avg_trip_distance`;
- `avg_fare_amount`.

Kui mõtled sellele dimensionaalse modelleerimise vaates, siis `pickup_zip` käitub siin nagu lihtne asukoha tunnus ja `distance_band` nagu teine kirjeldav tunnus. Me ei loo nende jaoks eraldi dimensioonitabeleid, kuid granulaarsuse sõnastamine aitab hoida tabeli mõtte selgena.

### Tee üks lihtne visualiseering

Kui kokkuvõttetabel on ees, tee sellest ka väike graafik.

1. jäta `display(summary)` tulemus lahti;
2. vali visualiseerimise vaade;
3. tee tulpdiagramm;
4. vali `pickup_zip` teljele `X`;
5. vali `trip_count` teljele `Y`.

Kui visualiseering läheb liiga tihedaks, filtreeri kõigepealt üks `distance_band` väärtus või kuva ainult need read, mille `trip_count` on suurim.

Selle sammu mõte ei ole teha täiuslikku aruannet. Eesmärk on näha, et notebook ei näita ainult ridu, vaid toetab ka kiiret esmast visualiseerimist.

## 7. Salvesta tulemus oma tabelisse

See samm tehakse notebooki `Python` lahtris.

Nüüd teed tänase praktikumi `load` osa. Salvestad saadud kokkuvõtte oma tabelisse skeemi `praktikum_05`.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# session_user() tagastab aktiivse kasutaja nime.
# regexp_replace(...) asendab sobimatud märgid alakriipsuga,
# et tabelinimi oleks turvalisem.
username_safe = spark.sql(
    "SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_') AS username"
).first()["username"]

# Tabeli enda nimi ilma catalogi ja skeemita.
target_table_name = f"user_{username_safe}_taxi_trip_summary"

# Koostame täieliku SQL-identifikaatori kujul catalog.schema.table.
# Iga osa on eraldi backtickides, et erimärgid ei tekitaks viga.
target_table_identifier = f"{catalog_identifier}.{schema_identifier}.`{target_table_name}`"

# write.mode("overwrite") tähendab:
# kui tabel on juba olemas, kirjutatakse see samanimelise uue sisuga üle.
# saveAsTable(...) salvestab DataFrame'i Databricksis tabelina.
summary.write.mode("overwrite").saveAsTable(target_table_identifier)

# print(...) näitab sulle loodud tabeli nime.
print(f"Loodi tabel: {target_table_identifier}")
```

Mida see teeb?

- võtab sinu kasutajanimest turvalise tabelinime osa;
- ehitab täieliku tabelinime kujul `catalog.schema.table`;
- paneb catalogi, skeemi ja tabeli nime SQL-is korrektsesse kujusse;
- kirjutab `summary` tulemuse tabeliks;
- kasutab `overwrite` režiimi, et saaksid sama sammu turvaliselt uuesti käivitada.

Oluline tähelepanek:

Databricks loob sellise tabeli vaikimisi `Delta Lake` formaadis. See tähendab, et tabeli taga kasutatakse `Parquet` andmefaile ja lisaks `Delta` logi.

Õnnestumise märk:

- väljundis kuvatakse täielik tabelinimi;
- veateadet ei tule.

Kui saad veateate, et `samples` alla ei saa kirjutada, siis kontrolli uuesti, et `workspace_catalog` ei oleks `samples`.

## 8. Kontrolli tulemust notebookis ja Catalog vaates

See samm tehakse kahes kohas:

- esmalt notebooki `Python` lahtris;
- seejärel Databricksi `Catalog` vaates.

Käivita notebookis järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# Loeme äsja loodud tabeli tagasi sisse SQL päringuga,
# et kontrollida salvestuse tulemust.
select_target_table_sql = f"SELECT * FROM {target_table_identifier} ORDER BY trip_count DESC"
display(spark.sql(select_target_table_sql))
```

Mida see teeb?

See loeb just loodud tabeli tagasi sisse ja näitab, et salvestus päriselt õnnestus.

Õnnestumise märk:

- näed samu veerge, mida nägid `summary` väljundis;
- ridu on vähemalt paar;
- tulemus tuleb sinu enda tabelist, mitte enam `samples` tabelist.

### Tee nähtavaks, et tabel on `Delta`

Praegu on oluline üks asi teadlikult üle kontrollida.

Sa salvestasid tabeli küll Databricksi, aga ilma lisasammuta ei pruugi olla ilmne, mis formaati see tabel kasutab.

Käivita järgmine lahter:

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# DESCRIBE DETAIL näitab tabeli tehnilisi omadusi,
# sealhulgas seda, mis formaati tabel kasutab.
describe_target_table_sql = f"DESCRIBE DETAIL {target_table_identifier}"
display(spark.sql(describe_target_table_sql))
```

Mida see teeb?

See näitab loodud tabeli tehnilisi detaile.

Mida väljundist otsida?

- veergu `format`;
- selle veeru väärtust `delta`.

Kui näed väärtust `delta`, siis on sul nüüd nähtav tõend, et salvestatud tabel on `Delta Lake` tabel.

Miks me siiski räägime `Parquet`-ist?

Sellepärast, et `Delta Lake` ei asenda `Parquet`-i täielikult. Databricksi ametliku dokumentatsiooni järgi laiendab `Delta Lake` `Parquet` andmefaile tehingulogiga. Lihtsas keeles tähendab see seda, et õppija töötab täna `Delta` tabeliga, aga selle all kasutatakse `Parquet` faile.

Seejärel ava vasakult `Catalog` ja otsi üles:

- oma workspace catalog;
- selle sees skeem `praktikum_05`;
- selle sees tabel nimega `user_<midagi>_taxi_trip_summary`.

Kui tabel on seal olemas, siis on sul töötav väike notebookipõhine töövoog valmis.

## 9. Käivita sama notebook job'ina

See samm tehakse Databricksi veebiliideses.

Seni jooksutasid notebooki käsitsi. Järgmisena teed sama töö korduvaks job'iks.

1. Mine tagasi sama notebooki vaatesse.
2. Vali notebooki ülaribal `Schedule`.
3. Kui selle notebooki jaoks ei ole veel ühtegi job'i, avaneb uue schedule'i loomise vaade.
4. Pane job'ile nimi, näiteks `praktikum5_taxi_summary_job`.
5. Vali lihtne ajakava, näiteks kord päevas.
6. Vali compute'iks serverless.
7. Loo schedule.
8. Ava uuesti `Schedule`.
9. Leia loodud job ja vali `Run now`.
10. Ava sama vaate kaudu job'i detailid ja kontrolli viimase käivituse tulemust.

Mida see samm teeb?

See näitab, et sama notebook ei ole ainult õppevahend. Sama notebook võib olla ka käivitatav töö.

Õnnestumise märk:

- job käivitub;
- run saab staatuse `Succeeded`;
- vajadusel saad avada jooksu detailid ja näha väljundit.

Kui nuppude nimed sinu tööruumis on veidi teised, otsi märksõnu `Schedule` ja `Run now`. Databricksi kasutajaliides muutub ajas, kuid põhimõte jääb samaks.

## 10. Seo nähtud töö ETL-iga

Nüüd vaata korraks tagasi kogu töövoole.

Selles praktikumis oli `ETL` järgmine:

- `Extract`: `spark.read.table("samples.nyctaxi.trips")`
- `Transform`: filtreerimine, `distance_band` veeru loomine, rühmitamine `pickup_zip` ja `distance_band` järgi ning mõõdikute arvutamine
- `Load`: `saveAsTable(...)`

See oli väike näide, aga loogika on sama ka suuremate tööde puhul.

Sa ei teinud lihtsalt üksikut päringut. Sa tegid korduva töövoo, millel on sisend, töötlus ja väljund.

Siit saab juba edasi liikuda keerukamate teemade juurde:

- rohkem allikaid;
- rohkem teisendusi;
- partitsioneerimine;
- suuremad andmemahud;
- eraldi orkestreeritud töövood.

## Kontrollpunktid

### Pärast notebooki loomist

- sul on olemas `Python` notebook;
- notebook on Databricksis avatud.

### Pärast compute'i ühendamist

- notebook näitab, et see on ühendatud;
- lihtne `print(...)` lahter töötab.

### Pärast skeemi loomist

- skeem `praktikum_05` on loodud;
- näed seda oma workspace catalogi all.

### Pärast sample-andmete lugemist

- `samples.nyctaxi.trips` avaneb;
- näed vähemalt 20 rida.

### Pärast teisendust

- `summary` väljundis on viis veergu;
- visualiseeringu saad luua sama väljundi pealt.

### Pärast tabeli salvestamist

- väljundis kuvatakse täielik tabelinimi;
- tabeli tagasilugemine muutujaga `target_table_identifier` töötab;
- tabel on Catalog vaates olemas.

### Pärast job'i käivitust

- job on loodud;
- vähemalt üks käivitus on staatusega `Succeeded`.

## Levinud vead ja lahendused

### Sümptom: notebook ei ühendu compute'iga

Tõenäoline põhjus:

- serverless compute ei ole veel valmis;
- Free Editioni kasutuspiir on ajutiselt täis.

Lahendus:

- oota veidi ja proovi uuesti;
- kontrolli, et notebook oleks päriselt `connected`;
- väldi väga suuri või pikki katsejookse.

### Sümptom: `Table or view not found`

Tõenäoline põhjus:

- tabeli nimi on vale;
- kasutad valet catalogi või skeemi;
- `target_table_identifier` väärtus ei saanud õigesti loodud.

Lahendus:

- kontrolli, et `samples.nyctaxi.trips` oleks kirjutatud täpselt nii;
- kontrolli, et `workspace_catalog` oleks sinu enda catalog, mitte `samples`;
- prindi vajadusel `target_table_identifier` uuesti välja.

### Sümptom: tabelit ei saa kirjutada

Tõenäoline põhjus:

- proovisid kirjutada `samples` catalogisse;
- kirjutasid catalogi nime valesti;
- skeem `praktikum_05` jäi loomata.

Lahendus:

- käivita uuesti `SHOW CATALOGS`;
- kontrolli, et skeem oleks loodud käsuga `CREATE SCHEMA IF NOT EXISTS ...`;
- ava kõrvale `Catalog` vaade;
- kasuta täielikku tabelinime kujul `catalog.schema.table`.

### Sümptom: skeemi loomisel tuleb õiguste viga

Tõenäoline põhjus:

- kasutasid valet catalogi;
- proovisid luua skeemi catalogisse, kuhu sul ei ole õigusi.

Lahendus:

- kasuta oma workspace catalogi, mitte `samples` catalogit;
- kontrolli catalogi nimi uuesti käsuga `SHOW CATALOGS`;
- kui töötad jagatud keskkonnas, küsi vajadusel juhendajalt või keskkonna haldurilt, millises catalogis tohib uusi skeeme luua.

### Sümptom: kopeerisid näite, mis on `Scala` või `R` keeles

Tõenäoline põhjus:

- vaatasid üldist Databricksi juhendit, mis ei olnud mõeldud Free Editioni jaoks.

Lahendus:

- kasuta selles praktikumis ainult `Python` näiteid;
- kui notebooki lahter ei näe välja nagu `Python`, loo uus `Python` lahter või uus `Python` notebook.

### Sümptom: otsid Spark UI-d või klastri seadeid

Tõenäoline põhjus:

- eeldasid, et Free Edition töötab nagu täisfunktsionaalne Databricksi ettevõtte tööruum.

Lahendus:

- arvesta, et Free Edition on serverless-only keskkond;
- selles praktikumis ei ole Spark UI vajalik;
- keskendu notebooki väljundile, Catalog vaatele ja job'i run detailidele.

## Kokkuvõte

Selles praktikumis tegid läbi oma esimese väikese Databricksi töövoo.

Sa:

- lõid `Python` notebooki;
- ühendasid selle serverless compute'iga;
- lugesid sample-andmeid;
- tegid `PySpark` teisenduse;
- salvestasid tulemuse oma tabelisse;
- käivitasid sama töö job'ina.

See töövoog on lihtne, aga oluline. Just selliste väikeste sammude kaudu saab selgeks, mida tähendab pilvepõhine andmetöötlus, miks `Parquet` ja `Delta Lake` on kasulikud ning miks hajussüsteemi teema on päris tööelus oluline.

## Valikulised lisaülesanded

### Lisaülesanne 1: teisenda miilid kilomeetriteks ja dollarid eurodeks

Praeguses lahenduses kasutad veerge `trip_distance` ja `fare_amount` nende algsel kujul.

Selles lisaülesandes täienda teisenduse sammu nii, et:

- sõidupikkus teisendatakse miilidest kilomeetriteks;
- hind teisendatakse dollaritest eurodeks;
- lõpptabelis oleksid mõõdikud juba uues ühikus.

Kasuta selle harjutuse jaoks kokkuleppelist kurssi ja teisendustegurit:

- `1 mile = 1.60934 km`
- `1 USD = 0.92 EUR`

Oluline märkus:

See eurokurss on selles ülesandes kokkuleppeline õppematerjali väärtus. See ei ole päring hetke kursile.

Sinu ülesanne on muuta sammu 6 koodi nii, et lõpptulemuses oleksid näiteks järgmised mõõdikud:

- `trip_count`
- `avg_trip_distance_km`
- `avg_fare_amount_eur`

Vihje:

Selleks sobivad hästi `withColumn(...)`, `F.col(...)`, korrutamine ja `F.round(...)`.

Kui teed selle muudatuse ära, sõnasta granulaarsus uuesti üle. Granulaarsus ise ei muutu.

See jääb endiselt:

`üks rida ühe pickup_zip ja distance_band kombinatsiooni kohta`

Muutuvad ainult mõõdikute ühikud ja nimed.

### Lisaülesanne 2: mõtle läbi andmekvaliteedi kontrollid

Andmetöötluse juures ei piisa ainult sellest, et kood käivitub. Sul peab olema ka mingi alus öelda, kas tulemus tundub usaldusväärne.

Mõtle oma lõpptabeli kohta vähemalt kolme järgmise kontrolli peale ja proovi need notebookis läbi teha:

- üheski reas ei tohi `trip_count` olla väiksem või võrdne nulliga;
- üheski reas ei tohi `avg_trip_distance_km` või `avg_fare_amount_eur` olla `NULL`;
- teisendatud vahemaa ja hind peavad jääma positiivseks;
- `pickup_zip` ei tohi olla tühi;
- sama `pickup_zip` ja `distance_band` kombinatsioon ei tohi tabelis korduda.

Kui tahad, kirjuta nende kontrollide jaoks eraldi väike kontrolllahter.

Näiteks võid küsida endalt:

- kas mõni mõõdik on negatiivne;
- kas mõni võtmekombinatsioon kordub;
- kas mõni oluline väli on tühi.

Selle lisaülesande mõte on harjutada seda, et iga andmetabeli juures tasub mõelda vähemalt paarile lihtsale kvaliteedikriteeriumile.

### Lisaülesanne 3: proovi Genie Code'i

#### Mis see on?

`Genie Code` on Databricksi tehisabiline koodi kirjutamiseks ja selgitamiseks.

See ei ole sama asi mis `Genie` AI/BI poolel. `Genie` aitab pigem andmeid loomulikus keeles küsida. `Genie Code` aitab notebookis ja SQL redaktoris koodi mõista, parandada ja luua.

#### Milleks see hea on?

`Genie Code` on kasulik siis, kui:

- tahad paluda olemasoleva koodi lühikest selgitust;
- tahad veateatele kiiret tõlgendust;
- tahad esimest mustandit `PySpark` koodist;
- tahad küsida, kuidas sama töö võiks olla loetavam või turvalisem.

Baastaseme õppija jaoks on see eriti kasulik siis, kui sa veel ei tea täpset süntaksit, aga saad juba aru, mida tahad teha.

Näiteks võid küsida:

- `Selgita seda PySpark koodi lühidalt.`
- `Mida teeb withColumn selles näites?`
- `Paku sellele koodile loetavam versioon.`

#### Millal peab ettevaatlik olema?

Siin on kolm olulist ettevaatuse kohta.

Esiteks, tehisabiline võib eksida.

Databricks ütleb ise, et AI-vastused võivad olla valed, segased või kasutaja soovi valesti mõista. Seega kontrolli alati vastus üle enne, kui selle põhjal koodi käivitad.

Teiseks, `Genie Code` kasutab vastuse koostamiseks konteksti.

Dokumentatsiooni järgi võib see saata mudelile sinu prompti, jooksva lahtri koodi, päringu või muud asjakohast metaandmestikku. `Agent mode` võib lisaks analüüsida lahtri väljundit ja lugeda tabelitest andmenäiteid. Seetõttu kasuta kursusel ainult ohutuid testandmeid.

Kolmandaks, `Agent mode` võib kasutaja loal koodi ka käivitada.

See on mugav, aga enne kinnitamist loe plaan ja muudatused läbi. Ära kinnita ettepanekuid automaatselt. Vaata enne üle, mida agent teha tahab.

#### Väike prooviharjutus

Kui sinu tööruumis on `Genie Code` nähtav, proovi järgmist:

1. ava notebooki kõrval `Genie Code` paneel;
2. kleebi sinna oma `summary` lahtri kood;
3. küsi: `Selgita seda koodi viies lühikeses punktis.`;
4. võrdle vastust omaenda selgitusega;
5. kui palud koodisoovitust, loe see enne kasutamist ise läbi.

Selle lisaharjutuse eesmärk ei ole delegeerida mõtlemist tehisabile. Eesmärk on õppida kasutama seda tööriista abilisena, mitte asendajana.

## Koristamine

Kui tahad praktikumi hiljem puhtalt uuesti teha, tasub koristamine lõpuni läbi teha.

### 1. Pane scheduled job pausile või kustuta see

See samm tehakse Databricksi veebiliideses.

1. Ava oma notebook.
2. Vali ülaribal `Schedule`.
3. Leia praktikumi job.
4. Kui tahad job'i alles hoida, aga mitte lasta sellel automaatselt joosta, vali `Pause`.
5. Kui tahad praktikumi sellest osast täielikult puhtaks teha, vali `Delete`.

Databricksi dokumentatsiooni järgi saad scheduled notebook job'i muuta, pausile panna, jätkata või kustutada.

Praktikumi mõttes on mõistlik mitte jätta schedule'iga job'i aktiivseks, kui sa seda enam ei vaja. Turvaline eeldus on, et job jääb alles seni, kuni paned selle ise pausile või kustutad.

### 2. Kustuta praktikumi skeem koos tabelitega

See samm tehakse notebooki `Python` lahtris või SQL redaktoris.

Loo uus lahter. Kleebi kogu koodiplokk ühte lahtrisse. Käivita see klahvidega `Shift+Enter`.

```python
# Kui tulid koristamise juurde hiljem tagasi,
# kirjuta oma workspace catalogi nimi uuesti siia.
workspace_catalog = "<kirjuta siia oma workspace catalogi nimi>"
workspace_schema = "praktikum_05"

# Koostame catalogi ja skeemi SQL-kujud eraldi muutujatesse.
catalog_identifier = f"`{workspace_catalog}`"
schema_identifier = f"`{workspace_schema}`"

# DROP SCHEMA ... CASCADE kustutab skeemi ja selle sees olevad tabelid.
drop_schema_sql = f"DROP SCHEMA IF EXISTS {catalog_identifier}.{schema_identifier} CASCADE"
spark.sql(drop_schema_sql)

print(f"Kustutati skeem: {catalog_identifier}.{schema_identifier}")
```

Mida see teeb?

- kustutab skeemi `praktikum_05`;
- kustutab selle all olevad tabelid ühe käsuga.

Oluline tähelepanek:

Databricksi dokumentatsiooni järgi kustutab `DROP SCHEMA ... CASCADE` Unity Catalogis skeemi objektid kohe, aga managed tabelite failid kustutatakse taustal 7 kuni 30 päeva jooksul. See on Databricksi enda hallatav koristusprotsess.

### 3. Kustuta notebook või kaust Workspace vaates

See samm tehakse Databricksi veebiliideses.

1. Ava vasakult `Workspace`.
2. Leia notebook, mille lõid selle praktikumi jaoks.
3. Vali `Move to Trash`.
4. Kui tahad selle kohe jäädavalt eemaldada, ava `Trash` ja vali `Empty Trash`.

Databricksi dokumentatsiooni järgi kustutatakse `Trash` kausta sisu jäädavalt 30 päeva pärast ka siis, kui sa seda käsitsi ei tühjenda.

Kui tahad hiljem sama notebooki uuesti kasutada, ära seda kustuta. Sel juhul piisab tavaliselt skeemi kustutamisest ja job'i pausile panemisest või kustutamisest.

## Kasutatud allikad

- Databricks Free Edition: <https://docs.databricks.com/aws/en/getting-started/free-edition>
- Databricks Free Edition limitations: <https://docs.databricks.com/aws/en/getting-started/free-edition-limitations>
- Serverless compute limitations: <https://docs.databricks.com/aws/en/compute/serverless/limitations>
- Create your first table and grant privileges: <https://docs.databricks.com/aws/en/getting-started/create-table>
- Load and transform data using Apache Spark DataFrames: <https://docs.databricks.com/aws/en/getting-started/dataframes>
- Manage schemas: <https://docs.databricks.com/aws/en/schemas/manage-schema>
- DROP SCHEMA: <https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-schema>
- Manage workspace objects: <https://docs.databricks.com/aws/en/workspace/workspace-objects>
- Databricks AI assistive features: <https://docs.databricks.com/aws/en/databricks-ai>
- Databricks AI assistive features trust and safety: <https://docs.databricks.com/aws/en/databricks-ai/databricks-ai-trust>
- Create and manage scheduled notebook jobs: <https://docs.databricks.com/aws/en/notebooks/schedule-notebook-jobs>
