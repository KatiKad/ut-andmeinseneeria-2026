# Praktikum 8: Reaalajas andmetöötlus. Kafka ja Spark Structured Streaming

## Eesmärk

Ehitada voogandmete (_streaming_) andmetoru, mis loeb sündmusi Apache Kafkast, töötleb neid Spark Structured Streamingu abil ning kirjutab tulemused Delta tabelisse. Praktikumi käigus tutvud Kafka põhikontseptsioonidega (teema (_topic_), partitsioon (_partition_), nihe (_offset_), tarbijagrupp (_consumer group_)), õpid kasutama sündmuse aja (_event time_) põhiseid akende agregatsioone koos vesimärgiga (_watermark_) ning näed, kuidas kontrollpunkt (_checkpoint_) tagab idempotentse taaskäivituse.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Käivitab Kafka maakleri KRaft režiimis ja loob teema (_topic_) soovitud partitsioonide arvuga.
- Selgitab partitsioonisisese järjekorra garantiid ja loeb tarbijagrupi mahajäämust (_consumer group lag_).
- Loob Spark Structured Streamingu päringu, mis loeb Kafkast (`readStream.format("kafka")`), parsib JSON-sõnumi ning kirjutab tulemuse väljundisse.
- Rakendab kattuvat (_tumbling_) ja libisevat (_sliding_) akent koos vesimärgiga sündmuse aja põhiseks agregeerimiseks.
- Võrdleb väljundirežiime (_output mode_): `append`, `complete`, `update`.
- Kirjutab voo Delta tabelisse, taaskäivitab päringu ja tõestab, et kontrollpunkt välistab andmete dubleerimise.
- Rikastab voogu staatilise andmestiku liitmisega (_streaming-static join_).
- Väljendab sama akenduse päringu nii DataFrame API kui ka Spark SQL kujul ning loeb `explain()` plaani.

## Ülevaade

| Osa | Sisu |
|-----|------|
| Demo | Kafka alused, struktureeritud voogtöötlus algusest lõpuni, akendega agregeerimine, keerukamad mustrid (Delta sink, voo ja staatilise andmestiku liitmine, Spark SQL võrdlus) |
| Ülesanded | Libisev aken vesimärgiga, väljundirežiimide võrdlus, Delta sink ja agregaadi salvestamine |

---

## Eeldused

- Docker Desktop on paigaldatud ja töötab.
- Kogemus Pythoni ja SQL-iga.
- Arusaam sündmustest ja avaldamise/tellimise (_publish/subscribe_) mudelist (vt baastaseme praktikum).
- Eelmiste praktikumide konteinerid on peatatud, et pordid 8888 ja 9092 oleksid vabad:

```bash
docker compose down
```

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Teema** (_topic_) | Kafka loogiline kanal, kuhu tootja (_producer_) avaldab sõnumid ja millest tarbija (_consumer_) neid loeb. |
| **Partitsioon** (_partition_) | Teema alamjaotus. Sõnumid jagunevad partitsioonide vahel. Iga partitsioon on järjestatud, kuid partitsioonide üleselt järjekorda ei garanteerita. |
| **Nihe** (_offset_) | Sõnumi järjekorranumber partitsiooni sees. Tarbija salvestab oma viimati loetud nihke, et tarbimist hiljem jätkata. |
| **Tarbijagrupp** (_consumer group_) | Tarbijate hulk, kes jagavad omavahel teema partitsioonid. Iga partitsiooni loeb grupi sees ainult üks tarbija. |
| **Mahajäämus** (_lag_) | Vahe partitsiooni viimase nihke ja tarbija viimase salvestatud nihke vahel. Näitab, kui palju sõnumeid on tarbijal töötlemata. |
| **Struktureeritud voogtöötlus** (_Structured Streaming_) | Sparki API voogandmete töötlemiseks. Voog käitub nagu lõputult kasvav DataFrame. |
| **Sündmuse aeg** (_event time_) | Ajatempel, mille tootja sõnumi kehasse paneb. See on aeg, mil sündmus reaalmaailmas toimus. |
| **Töötluse aeg** (_processing time_) | Ajatempel hetkel, mil Spark sõnumi vastu võtab. Erineb sündmuse ajast, sest sõnumid võivad hilineda. |
| **Kattuvuseta aken** (_tumbling window_) | Sama suurusega ja kattuvuseta aknad. Iga sündmus kuulub täpselt ühte aknasse. |
| **Libisev aken** (_sliding window_) | Sama suurusega aknad, mis kattuvad. Sündmus võib kuuluda mitmesse aknasse korraga. |
| **Vesimärk** (_watermark_) | Spark loobub vanade akende olekust, kui sündmuse aja maksimum on aknaga lõpust kaugemal kui vesimärgi piir. Hoiab mälukulu kontrolli all. |
| **Väljundirežiim** (_output mode_) | Määrab, mida päring igal käivitamisel väljundisse kirjutab: `append` (ainult uued read), `complete` (kogu tulemustabel), `update` (ainult muutunud read). |
| **Kontrollpunkt** (_checkpoint_) | Kataloog, kuhu Spark salvestab päringu seisundi (loetud nihked, agregaatide olek). Taaskäivitusel jätkab päring sealt, kus eelmine kord pooleli jäi. |
| **Voo ja staatilise andmestiku liitmine** (_streaming-static join_) | Voogu rikastatakse staatilise tabeliga (näiteks otsingutabel). Staatiline pool laetakse mällu üks kord ja jagatakse (_broadcast_) töötajatele. |
| **Delta tabel** (_Delta table_) | ACID-tehinguid toetav tabelivorming Spark `parquet` failidel. Võimaldab `UPDATE`, `MERGE`, ajas tagasiminekut (_time travel_) ja olekuajalugu (`DESCRIBE HISTORY`). |

## Olulised viited

* **Structured Streaming + Kafka Integration Guide**
https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
Ametlik juhend Kafka konnektorist Sparkis.

* **Structured Streaming Programming Guide**
https://spark.apache.org/docs/latest/streaming/index.html
Põhjalik tutvustus voogtöötluse mudelist, eriti sündmuse aja, vesimärkide ja väljundirežiimide jaotised.

* **Apache Kafka dokumentatsioon**
https://kafka.apache.org/documentation/
Kafka enda kontseptsioonide ja CLI tööriistade viide.

* **Delta Lake**
https://delta.io/
Delta tabelite vorming, ACID, ajas tagasiminek (_time travel_).

---

## Keskkond

### Teenused

| Teenus | Konteiner | Kirjeldus |
|--------|-----------|-----------|
| Kafka broker | `praktikum8_kafka` | Apache Kafka 4.2.0 KRaft režiimis (ilma ZooKeeperita), port 9092 |
| Jupyter + PySpark | `praktikum8_jupyter` | Spark 4.1.1 ja Scala 2.13. Pordid 8888 (Jupyter) ja 4040 (Spark UI) |

### Arhitektuur

```
┌─────────────────────────────────────────────────┐
│  Docker Compose võrk                            │
│                                                 │
│  ┌──────────────────┐    kafka:9092             │
│  │  kafka           │◄────────────────────────┐ │
│  │  KRaft maakler   │    KRaft, üks sõlm      │ │
│  └──────────────────┘                         │ │
│                                               │ │
│  ┌────────────────────────────────────────┐   │ │
│  │  jupyter (pyspark-notebook)            │───┘ │
│  │  • kafka-python-ng (Pythoni klient)    │     │
│  │  • PySpark + spark-sql-kafka konnektor │     │
│  │  • delta-spark (Delta Lake)            │     │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
         ▲                   ▲
    localhost:8888       localhost:4040
    (Jupyter UI)         (Spark UI)
```

### Seadistamine

1. Kopeeri `.env.example` failist `.env`:

```bash
cp .env.example .env
```

> **NB!** `.env` fail võib tulevikus sisaldada saladusi ja seetõttu on see lisatud `.gitignore`-i, et see Giti repositooriumisse ei satuks.

2. Käivita teenused:

```bash
docker compose up -d
```

Esimesel käivitusel laeb Docker alla nii Kafka kui ka PySparki tõmmised. Kui notebook sees käivitatakse `pip install delta-spark`, laeb Spark startup ajal alla ka Delta paketi (`io.delta:delta-spark_2.13:4.2.0`) ja Kafka konnektori (`org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1`). See võtab esimesel korral mõne minuti.

3. Kontrolli, et teenused töötavad:

```bash
docker compose ps
```

Oodatav tulemus: mõlemad teenused (`kafka`, `jupyter`) staatuses `running` (või `Up`).

4. Ava Jupyter brauseris:

```
http://localhost:8888
```

Kui sisselogimisleht küsib token-it, sisesta `praktikum` (või väärtus, mille panid `.env`-i `JUPYTER_TOKEN` muutujasse).

5. Spark UI avaneb pärast esimese SparkSession-i loomist aadressil:

```
http://localhost:4040
```

### Ühendused

| Teenus | Host (konteinerist) | Port (hostist) |
|--------|---------------------|----------------|
| Kafka broker | `kafka:9092` | 9092 |
| Jupyter | `jupyter:8888` | 8888 |
| Spark UI | (jupyter-konteineris) | 4040 |

> Kafka maakleriga ühendutakse Sparkist hostinime `kafka` kaudu, kuna mõlemad konteinerid on samas Docker Compose võrgus.

---

## Kafka CLI viide

Notebookis kasutame Kafkaga suhtlemiseks `kafka-python-ng` Pythoni teeki. Sama tegevust saab teha ka käsurealt CLI-tööriistadega. Käivita käsud **hosti terminalis** (mitte Jupyteri konteineri sees), sest `docker` käsk ei ole konteineri sees saadaval.

| Tegevus | Käsk |
|---------|------|
| Loo teema | `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic sensor-events --partitions 3 --replication-factor 1"` |
| Loetle teemad | `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list"` |
| Kirjelda teemat | `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic sensor-events"` |
| Konsoolitootja | `docker exec -it praktikum8_kafka bash -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic sensor-events"` |
| Konsoolitarbija | `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic sensor-events --from-beginning"` |
| Tootja võtmega (vorming `võti:väärtus`) | `docker exec -it praktikum8_kafka bash -c "/opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic sensor-events --reader-property parse.key=true --reader-property key.separator=:"` |
| Tarbijagrupi mahajäämus | `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <grupi-id>"` |

> Loo paar sõnumit sama võtmega ja seejärel tarbi iga partitsiooni eraldi (`--partition 0`, `--partition 1`, ...). Näed, et sama võtmega sõnumid satuvad alati ühte partitsiooni. Järjekord on garanteeritud partitsiooni sees, mitte partitsioonide üleselt.

Nt: `docker exec praktikum8_kafka bash -c "/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic sensor-events --partition 0 --from-beginning"`

---

## Demo

Ava Jupyter ja seal fail `work/praktikum8_voogandmed.ipynb`. Käivita lahtrid järjekorras. Notebook on jagatud nelja ossa.

### 1. Kafka alused

Alusta Kafka teema loomisest (3 partitsiooni). Saada üheksa võtmega sõnumit (kolme sensori kohta kolm sõnumit). Tarbi sõnumid ja vaatle, millisesse partitsiooni iga sõnum jõudis. Lõpuks vaata tarbijagrupi nihkeid.

Kontrollikoht: sama `sensor_id` väärtusega sõnumid jõuavad alati samasse partitsiooni. See järeldub Kafka vaikejaoturist (_default partitioner_), mis arvutab partitsiooni võtme räsist (_hash_).

### 2. Struktureeritud voogtöötlus algusest lõpuni

Loe Kafka teemast voog (`readStream.format("kafka")`). Vaata Kafka DataFrame'i toorskeemi. Parsi JSON väärtus eraldi veergudeks. Kirjuta voog **mälusihtkohta** ja vaata tulemust `spark.sql("SELECT * FROM raw_events")` kaudu.

> Mälusihtkoht on **ainult silumiseks** mõeldud. Toodangus kasutatakse failipõhist sihtkohta, Delta tabelit, andmebaasi, jne.

Demo ajal toodame jooksvalt uusi sõnumeid ja jälgime, kuidas need pärast järgmist käivitustsüklit (`processingTime="3 seconds"`) tabelisse lisanduvad.

### 3. Akendega agregeerimine sündmuse aja alusel

Loo voo päring, mis grupeerib sõnumeid 1-minutilise kattuvuseta akna ja sensori järgi. Käivita see kahel viisil:

- **`complete` režiim ilma vesimärgita.** Spark hoiab kõikide akende olekut igavesti. Hilinenud sündmus tekitab vana akna ümberarvutuse. Sobib õppe-eesmärgil ja lühiajaliseks ülevaateks; tootmises tekitab mälulekke ohu.
- **`update` režiim 5-minutilise vesimärgiga.** Spark loobub akna olekust, kui see on vesimärgi piirist väljas. Liiga hilja saabunud sündmused visatakse vaikimisi kõrvale.

#### Arhitektuuriotsus: miks `update` koos vesimärgiga, mitte `complete` ilma vesimärgita?

1. **Probleem.** Voo agregeerimisel kasvab Sparki olekuhoidla (_state store_) iga uue akna lisandumisel. Pikaajalises päringus võib mälukasutus muutuda piiravaks.
2. **Variandid.** (a) `complete` ilma vesimärgita: lihtne, säilitab kõik aknad, alati täielik tulemus, mälu kasvab piiramatult. (b) `update` koos vesimärgiga: ainult muutunud read, mälu kontrollitud, hilinenud andmed üle vesimärgi langevad maha.
3. **Valik ja põhjendus.** `update` koos vesimärgiga. Tootmises on mälu kontrolli all hoidmine kriitiline ja pisike osa hilinenud sündmusi on tavaliselt aktsepteeritav kompromiss.
4. **Kompromissid.** Hilinenud sündmused, mis ületavad vesimärgi piiri, kaovad. Vesimärgi suurus tuleb valida domeeni järgi: kui sündmused võivad hilineda kuni 10 minutit, võta vesimärgiks 10 minutit, mitte 1.

### 4. Keerukamad mustrid

#### 4.1. Kirjutamine Delta tabelisse ja kontrollpunkti taaskäivitus

Kirjuta voog Delta tabelisse `/tmp/bronze`. Peata päring. Käivita sama päring uuesti **sama kontrollpunktiga**. Võrdle ridade arvu enne ja pärast taaskäivitust.

Kontrollikoht: `count_after == count_before` (kui vahepeal uusi sõnumeid juurde ei tooda). Kontrollpunkt salvestab töödeldud nihked. Päring jätkab sealt, kus eelmine kord pooleli jäi, isegi kui `startingOffsets` on endiselt `earliest`.

Lisaks vaatame Delta funktsioone: `DESCRIBE HISTORY` näitab versioonide ajalugu, `option("versionAsOf", N)` võimaldab lugeda vana versiooni (ajas tagasiminek).

#### 4.2. Voo ja staatilise andmestiku liitmine

Loo staatiline otsingutabel (`sensor_id` → asukoht, sensori tüüp). Liida see voo sõnumitega `F.broadcast` abil. See muster vastab **rikastamisele** (_enrichment_) hõbedakihis (_silver layer_).

Pane tähele: staatiline pool loetakse päringu käivitumisel üks kord. Lähteandmete hilisemad muudatused jooksva päringu sisse ei jõua.

#### 4.3. Spark SQL ja DataFrame API võrdlus

Loo voo DataFrame'ist ajutine vaade `createOrReplaceTempView("sensor_voog")`. Kirjuta sama akenduse päring kahel kujul:

- DataFrame API: `df.groupBy(F.window(...), "sensor_id").agg(F.avg(...))`
- Spark SQL: `spark.sql("SELECT window(event_time, '1 minute'), sensor_id, AVG(temperature) FROM sensor_voog GROUP BY 1, 2")`

Käivita mõlemal `.explain()`. Plaanid on identsed, sest Catalyst optimeerija ühtlustab need. Valik DataFrame API ja SQL-i vahel on stiili küsimus, mitte jõudluse: kasuta seda, mis on tiimi koodibaasis loetavam.

---

## Ülesanded

Vastusenäidised jagame hiljem GitHubis. Soovitus: ürita kõigepealt ise lahendada.

### Ülesanne 1: Libisev aken vesimärgiga

Kirjuta voo päring, mis:

1. Loeb teemast `sensor-events` (`startingOffsets="latest"`).
2. Rakendab libisevat akent suurusega **2 minutit** ja sammuga **30 sekundit** veerule `event_time`.
3. Grupeerib `sensor_id` järgi ja arvutab `min(temperature)`, `max(temperature)`, `count`.
4. Lisab vesimärgi **3 minutit**.
5. Kirjutab mälusihtkohta `update` režiimis.
6. Toodab 10 sündmust ja kuvab tulemustabeli.
7. Toodab 5 hilinenud sündmust (5 minutit minevikus, vesimärgi piires) ja kuvab tabeli uuesti. Kas mõni aken uuenes?
8. Peatab voo.

**Vihje.** `F.window(time_col, windowDuration, slideDuration)` võtab kolmandaks argumendiks libiseva sammu.

**Arutelu.** Mitu aknarida tekib ühe sündmuse kohta? Miks? Millal eelistada libisevat akent kattuvale?

### Ülesanne 2: Väljundirežiimi võrdlus

Käivita sama 1-minutiline kattuvuseta akenduse päring kahel korral, mõlemal vesimärk 5 minutit:

- üks `complete` režiimis (näiteks päringu nimi `windowed_complete_ex`),
- teine `update` režiimis (`windowed_update_ex`).

Sammud:

1. Tooda 6 sündmust käesolevas minuti aknas.
2. Kuva mõlemast memory tabelist tulemus.
3. Tooda 3 sündmust juurde **samasse minuti aknasse**.
4. Kuva mõlemast tabelist tulemus uuesti.

**Arutelu.** Kui palju ridu on igas tabelis pärast 4. sammu? Kumb režiim väljastab muutumatuid aknaid uuesti? Millal eelistada `update` režiimi tootmises?

### Ülesanne 3: Delta sink ja agregaadi salvestamine

Ehita kahekihiline andmetoru:

1. **Hõbedakiht** (_silver_): liida voog staatilise otsingutabeliga (nagu demo osas 4.2). Kirjuta rikastatud sündmused Delta tabelisse `/tmp/silver_events` koos kontrollpunktiga `/tmp/chk-silver`.
2. **Kuldkiht** (_gold_): kasuta `foreachBatch` mustrit. Iga mikropartii (_micro-batch_) sees:
   - arvuta sensori ja minuti kaupa kokkuvõte (`avg(temperature)`, `count`),
   - tee `MERGE` Delta tabelisse `/tmp/gold_aggregates` (uuendus olemasoleva (sensor, minut) puhul, lisamine uue puhul).
3. Peata mõlemad päringud. Käivita silverkihi päring sama kontrollpunktiga uuesti ja kontrolli, et `silver_events` ridade arv ei muutunud.
4. Loe `gold_aggregates` ja kuva tulemused. Käivita ka `spark.sql("DESCRIBE HISTORY delta.\`/tmp/gold_aggregates\`")` ja vaata versioonide ajalugu.

**Arutelu.** Miks me `gold` tabelis kasutame `MERGE`-i ja mitte `append`-i? Mis juhtuks, kui `silver_events` kontrollpunkt kustutada enne taaskäivitust?

---

## Tõrkeotsing

**Sümptom.** `docker compose up -d` lõppeb veaga "port is already allocated" pordi 8888 või 9092 kohta.

- **Diagnostika.** Käivita `docker ps` ja vaata, milline konteiner porti hõivab.
- **Lahendus.** Peata teine konteiner: `docker compose down` selle praktikumi kataloogis, kus port hõivatud on. Alternatiiv: muuda `compose.yml`-s pordi mappimist.

**Sümptom.** Notebooki esimese lahtri (`SparkSession` loomine) käivitamisel jookseb Spark mitu minutit ja siis viskab vea konnektori paketi laadimisel.

- **Diagnostika.** Vaata Jupyteri konteineri logisid: `docker logs praktikum8_jupyter`. Kontrolli, et hostil on internetiühendus (Spark laeb pakette Maven Central-ist).
- **Lahendus.** Käivita lahter uuesti. Esimese korralike laadimiste järel on paketid kohalikus `~/.ivy2` vahemälus ja järgmised käivitamised on kiired.

**Sümptom.** `KafkaError: NoBrokersAvailable`.

- **Diagnostika.** `docker compose ps` peab näitama `kafka` staatuses `Up`. Käivita `docker exec praktikum8_kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list`. Kui see ei tööta, vaata `docker logs praktikum8_kafka`.
- **Lahendus.** Anna Kafkale rohkem aega käivituseks (KRaft maakleril võtab esimene käivitus 10 kuni 20 sekundit). Kui Kafka ei käivitu üldse, eemalda olemasolev maht ja proovi uuesti: `docker compose down -v && docker compose up -d`.

**Sümptom.** Pärast notebooki taaskäivitamist näitab voo päring, et `startingOffsets` valikut eiratakse ja päring alustab keskelt.

- **Diagnostika.** See on oodatav käitumine. Kontrollpunkt sisaldab töödeldud nihkeid ja võidab `startingOffsets` konfiguratsiooni üle.
- **Lahendus.** Kui soovid päringut tõesti algusest taaskäivitada, kustuta kontrollpunkti kataloog (`shutil.rmtree("/tmp/chk-...", ignore_errors=True)`) ja seejärel käivita päring uuesti.

**Sümptom.** `delta-spark` paketi import või `configure_spark_with_delta_pip` viskab vea, mis viitab Spark versioonide mismatchile.

- **Diagnostika.** Kontrolli notebookis Sparki versiooni: `print(spark.version)`. Eeldus on `4.1.1`. Vaata Delta Lake'i ühilduvusmaatriksit aadressil https://docs.delta.io/latest/releases.html.
- **Lahendus.** Kui Delta versioon ei ühildu, kohanda paketi versiooni `spark.jars.packages` konfiguratsioonis (notebooki esimene lahter). Vaikimisi on praktikumis kasutusel `io.delta:delta-spark_2.13:4.2.0`.

