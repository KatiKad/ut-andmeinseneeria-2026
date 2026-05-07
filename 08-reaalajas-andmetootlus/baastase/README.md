# Praktikum 8: Reaalajas andmetöötlus Celery ja Redis abil

## Sisukord

- [Praktikumi eesmärk](#praktikumi-eesmärk)
- [Õpiväljundid](#õpiväljundid)
- [Hinnanguline ajakulu](#hinnanguline-ajakulu)
- [Eeldused](#eeldused)
- [Enne alustamist](#enne-alustamist)
- [Praktikumi failid](#praktikumi-failid)
- [Miks see teema on oluline?](#miks-see-teema-on-oluline)
- [Miks kasutame siin Celeryt ja Redist?](#miks-kasutame-siin-celeryt-ja-redist)
- [Uued mõisted](#uued-mõisted)
- [Soovitatud töötee](#soovitatud-töötee)
- [1. Ava praktikumi kaust](#1-ava-praktikumi-kaust)
- [2. Loo `.env` fail](#2-loo-env-fail)
- [3. Vaata üle teenused](#3-vaata-üle-teenused)
- [4. Käivita keskkond](#4-käivita-keskkond)
- [5. Kontrolli tühja algseisu](#5-kontrolli-tühja-algseisu)
- [6. Avalda veebipoe sündmused](#6-avalda-veebipoe-sündmused)
- [7. Vaata, mida worker tegi](#7-vaata-mida-worker-tegi)
- [8. Peata worker ja vaata järjekorda](#8-peata-worker-ja-vaata-järjekorda)
- [9. Proovi kordustöötlust](#9-proovi-kordustöötlust)
- [10. Võrdle sündmuse aega ja töötluse aega](#10-võrdle-sündmuse-aega-ja-töötluse-aega)
- [11. Ehita ajakna koondid](#11-ehita-ajakna-koondid)
- [12. Võrdle live-koondit pakktöötlusega](#12-võrdle-live-koondit-pakktöötlusega)
- [13. Proovi vigast sündmust](#13-proovi-vigast-sündmust)
- [14. Seos edasijõudnute Kafka praktikumi teemaga](#14-seos-edasijõudnute-kafka-praktikumi-teemaga)
- [Kontrollpunktid](#kontrollpunktid)
- [Levinud vead ja lahendused](#levinud-vead-ja-lahendused)
- [Kokkuvõte](#kokkuvõte)
- [Valikulised lisaharjutused](#valikulised-lisaharjutused)
- [Koristamine](#koristamine)

## Praktikumi eesmärk

Selle praktikumi eesmärk on teha läbi väike sündmuspõhine töövoog, kus veebipoe müügisündmus liigub taustatöö kaudu analüütika tabelitesse.

Kasutame nelja teenust:

- PostgreSQL-i andmebaas hoiab sündmuste logi ja analüütika tabeleid;
- Redis (https://redis.io/) on sõnumimaakler ehk järjekord;
- Celery worker ehk töötegija (https://docs.celeryq.dev/en/stable/) võtab Redisest tööülesanded;
- Pythoni käsukonteiner simuleerib veebipoodi.

Praktikum ei asenda Apache Kafka teemat. Siin õpime esmalt selgeks tootja, maakleri, worker'i, sündmuse aja ja idempotentsuse põhiloogika. Edasijõudnute praktikumis tehakse sama teema logipõhise voogedastusplatvormiga Apache Kafka ja Apache Spark Structured Streaming abil.

## Õpiväljundid

Praktikumi lõpuks oskad:

- selgitada, mis on sündmus ja miks see on reaalajalähedase töötluse põhiüksus;
- käivitada väikese Celery + Redis + PostgreSQL keskkonna `docker compose` abil;
- selgitada, mida teevad teenused `db`, `redis`, `app` ja `worker`;
- avaldada veebipoe müügisündmuseid Pythoni käsuga;
- jälgida, kuidas Celery worker töötleb Redise järjekorras olevaid tööülesandeid;
- kontrollida `SQL`-iga, millised sündmused on avaldatud, järjekorda saadetud, töödeldud või vigased;
- selgitada, miks sama sündmuse korduv töötlemine ei tohi teha topeltridu;
- eristada sündmuse aega ja töötluse aega;
- ehitada lihtsa 5 minuti akna põhise müügikoondi;
- võrrelda reaalajalähedast live-koondit ehk jooksvalt uuenevat koondit pakktöötlusega.

## Hinnanguline ajakulu

Arvesta umbes 2 kuni 2,5 tunniga.

See aeg jaguneb ligikaudu nii:

- 20 min keskkonna ja teenuste mõistmiseks;
- 25 min esimeste sündmuste avaldamiseks ja worker'i töö vaatamiseks;
- 25 min järjekorra, worker'i peatamise ja kordustöötluse proovimiseks;
- 25 min sündmuse aja, töötluse aja ja akende võrdlemiseks;
- 20 min pakktöötluse võrdluseks ja vigase sündmuse proovimiseks;
- 15 min kokkuvõtteks ja lisaharjutuste valimiseks.

## Eeldused

Sul on vaja:

- `VS Code`-i (`Visual Studio Code`) või GitHub Codespacesit;
- terminali;
- töötavat Dockeri keskkonda;
- selle repositooriumi faile.

Kasuks tuleb, kui varasemate baastaseme praktikumide põhjal on tuttavad:

- õige praktikumi kausta avamine;
- `.env` faili loomine `.env.example` põhjal;
- `docker compose up -d --build`;
- `docker compose exec ...` käsud;
- `psql` ehk PostgreSQL-i käsureakliendi abil `SQL`-faili käivitamine;
- 4. praktikumi mõte, et töövoog peab olema jälgitav ja korduskäivitatav.

Kui mõni neist sammudest on veel ebakindel, vaata vajadusel uuesti:

- [Praktikum 1: PostgreSQL-iga ühenduse loomine ja esimese CSV-faili laadimine](../../01-andmeinseneeria-alused/baastase/README.md)
- [Praktikum 4: Andmetorude orkestreerimine kohaliku `cron`-töövooga](../../04-andmetorude-orkestreerimine/baastase/README.md)
- [Praktikum 6: Andmekvaliteet ja andmehaldus](../../06-andmekvaliteet-ja-haldus/baastase/README.md)

## Enne alustamist

### Soovitatud keskkond

Selle praktikumi jaoks sobib hästi järgmine tööviis:

- ava kaust `08-reaalajas-andmetootlus/baastase` `VS Code`-is;
- kasuta `VS Code`-i sisseehitatud terminali;
- hoia lahti failid `README.md`, `compose.yml`, `scripts/webshop_demo.py` ja `scripts/celery_app.py`;
- käivita käsud hosti terminalist, kui juhendis ei ole öeldud teisiti.

Host tähendab sinu arvutit või Codespace'i tööruumi. Konteiner tähendab Dockeri sees töötavat teenust.

Selles praktikumis on neli konteinerit:

- `db` on PostgreSQL-i andmebaas;
- `redis` on Celery sõnumimaakler;
- `app` on käsukonteiner, kust käivitad veebipoe sündmuste käske ja `psql` kontrolle;
- `worker` on Celery worker, mis töötab taustal ja töötleb Redise järjekorda.

Kõik terminalikäsud käivitatakse hosti terminalis.

### Käsud eri terminalides

Selles juhendis on käsud kirjutatud nii, et need töötaksid samal kujul:

- macOS-i ja Linuxi terminalis;
- Git Bashis;
- Windows PowerShellis;
- GitHub Codespacesi terminalis.

Kasutame ühe rea käske ja suhtelisi teid, näiteks `scripts/01_check_stream.sql`.

See on teadlik valik. Kui anda Git Bashis Dockerile konteineri absoluutne tee, näiteks `/app/scripts/...`, võib Git Bash proovida seda oma Windowsi teeks ümber tõlgendada. Suhteline tee töötab siin paremini, sest `app` konteineri töökaust on juba `/app`.

Kui käsk:

```bash
cp .env.example .env
```

ei tööta sinu PowerShellis, kasuta sama tegevuse jaoks:

```powershell
Copy-Item .env.example .env
```

Kui töötad GitHub Codespacesis, siis on praktikumi kaust tavaliselt siin:

```text
/workspaces/ut-andmeinseneeria-2026/08-reaalajas-andmetootlus/baastase
```

### Puhas algus

See praktikum kasutab hostis PostgreSQL porti `5438`.

Redis töötab ainult Docker Compose võrgu sees. Selle porti ei avata hostile, sest sa ei pea Redis käsureaklienti eraldi kasutama.

Kui oled seda praktikumi varem käivitanud ja tahad täiesti puhast algust, kasuta juhendi lõpus olevat käsku:

```bash
docker compose down -v
```

See kustutab ka andmebaasi mahu. Järgmisel käivitamisel luuakse tabelid uuesti.

## Praktikumi failid

Kõik allpool toodud suhtelised failiteed eeldavad, et asud kaustas `08-reaalajas-andmetootlus/baastase`.

- [`compose.yml`](./compose.yml) kirjeldab andmebaasi, Redise, käsukonteineri ja Celery worker'i
- [`.env.example`](./.env.example) sisaldab vaikimisi andmebaasi ja Celery ühenduse väärtusi
- [`.gitignore`](./.gitignore) hoiab `.env` faili gitist väljas
- [`Dockerfile.app`](./Dockerfile.app) ehitab Pythoni konteineri, kus on Celery, PostgreSQL-i klient ja vajalikud teegid
- [`init/01_create_objects.sql`](./init/01_create_objects.sql) loob praktikumi skeemid ja tabelid
- [`source_data/products.csv`](./source_data/products.csv) sisaldab veebipoe tooteid `CSV` kujul (`Comma-Separated Values`, komadega eraldatud tekstifail)
- [`source_data/stores.csv`](./source_data/stores.csv) sisaldab veebipoe poode `CSV` kujul
- [`scripts/celery_app.py`](./scripts/celery_app.py) sisaldab Celery worker'i tööülesannet, mis töötleb ühe sündmuse
- [`scripts/webshop_demo.py`](./scripts/webshop_demo.py) loob müügisündmuseid ja saadab tööülesandeid Redises olevasse Celery järjekorda
- [`scripts/01_check_stream.sql`](./scripts/01_check_stream.sql) kontrollib sündmuste, tööülesannete ja live-koondi hetkeseisu
- [`scripts/02_build_time_windows.sql`](./scripts/02_build_time_windows.sql) ehitab 5 minuti akna koondid sündmuse aja ja töötluse aja põhjal
- [`scripts/03_compare_batch_and_stream.sql`](./scripts/03_compare_batch_and_stream.sql) võrdleb live-koondit pakktöötlusega
- [`scripts/04_check_worker_state.sql`](./scripts/04_check_worker_state.sql) koondab worker'i oleku ja live-koondi kontrollpäringud
- [`scripts/05_check_idempotency.sql`](./scripts/05_check_idempotency.sql) kontrollib, et kordustöötlus ei tekitanud topeltridu
- [`scripts/06_check_event_time.sql`](./scripts/06_check_event_time.sql) võrdleb sündmuse aega ja töötluse aega
- [`scripts/07_check_bad_events.sql`](./scripts/07_check_bad_events.sql) kuvab vigaste sündmuste tabeli viimased read
- [`scripts/99_reset.sql`](./scripts/99_reset.sql) tühjendab praktikumi tabelid

## Miks see teema on oluline?

Paljud töövood ei sobi hästi mudelisse, kus üks pikk skript teeb kõik kohe ära.

Näiteks veebipoes ei taha me ostu kinnitamise hetkel kõiki kõrvaltegevusi samas protsessis teha:

- analüütika koondi uuendamine;
- teavituse saatmine;
- püsikliendi punktide arvestus;
- arve PDF-faili loomine;
- riskikontrolli või kvaliteedikontrolli lisasamm.

Need tegevused võivad toimuda taustal. See teeb kasutaja jaoks põhitegevuse kiiremaks ja süsteemi paindlikumaks.

Selles praktikumis võtame neist ühe: müügisündmus jõuab taustatöö kaudu analüütika tabelitesse.

See ei ole ainus võimalik näide, kuid see on hea õppenäide, sest:

- see seostub 4. ja 6. praktikumi veebipoe andmetega;
- tulemust saab kohe `SQL`-iga kontrollida;
- sama sündmust saab võrrelda hilisema pakktöötlusega;
- kordustöötluse korral on topeltridade risk väga nähtav.

## Miks kasutame siin Celeryt ja Redist?

`Celery` on Pythoni maailmas levinud taustatööde tööriist. `Redis` on sageli kasutatav maakler, kuhu Celery paneb tööülesanded ootele.

Selline taustatööde muster on tööelus tavaline.

Näited:

- veebirakendus paneb aruande loomise taustatööks;
- pildid töödeldakse pärast üleslaadimist eraldi worker'is;
- e-kirjad või teavitused saadetakse järjekorra kaudu;
- müügisündmused töödeldakse analüütika vaatesse.

Oluline piir:

Celery + Redis on siin järjekorrapõhine lahendus. See ei ole Apache Kafka asendus.

Apache Kafka on logipõhine voogedastusplatvorm. Kafka puhul jäävad sõnumid logisse alles ja tarbijad loevad neid oma nihke ehk offseti järgi. Seda katab edasijõudnute praktikum.

Selles praktikumis hoiab Redis järjekorda mälus. `compose.yml` käivitab Redise ilma püsiva salvestuseta. See tähendab, et Redise järjekord sobib ajutiste tööülesannete hoidmiseks, mitte sündmuste ajaloo talletamiseks. Sündmuste nähtav ja kontrollitav ajalugu on PostgreSQL-i tabelis `stream.event_log`.

Kui `redis` konteiner ei tööta, ei saa publisher Celery tööülesannet järjekorda saata. Praeguses näites võib sündmus olla juba tabelisse `stream.event_log` kirjutatud, kuid selle olek jääb `published` ja rida ei ilmu tabelisse `stream.task_dispatch_log`. See ei ole selles praktikumis eraldi katsetatav harjutus, vaid töökindluse tähelepanek: järjekorrapõhises töövoos on maakler eraldi sõltuvus, mille tõrkega peab päris süsteemis arvestama.

PostgreSQL-i sündmuste logi aitab seda töövoogu nähtavaks teha. Nii näed `SQL`-iga:

- mis sündmus loodi;
- millal see järjekorda saadeti;
- millal worker selle töötles;
- kas sündmus õnnestus või kukkus läbi.

## Uued mõisted

### Sündmus

Andmetöötluses ei piisa alati päeva lõpu koondist. Sageli tahame talletada ka üksikuid juhtumeid kohe siis, kui need toimuvad.

Sündmus on kirje millegi toimumise kohta kindlal ajahetkel.

Näide:

`order_created` sündmus tekib siis, kui veebipoes kinnitatakse ost.

Tehniliselt on selle praktikumi sündmus rida tabelis `stream.event_log`. Sündmuse sisu on `JSON` kujul väljas `payload`. `JSON` tähendab `JavaScript Object Notation`; see on levinud tekstikuju võtme-väärtuse paaridega andmete esitamiseks.

### Publisher

Sündmusest pole palju kasu, kui see jääb ainult selle tekitanud programmi sisse. Keegi peab selle teistele süsteemidele nähtavaks tegema.

Publisher on protsess, mis avaldab sündmuse.

Näide:

Selles praktikumis on publisher käsk `python scripts/webshop_demo.py publish`. See kirjutab sündmuse PostgreSQL-i ja saadab Celery tööülesande Redise järjekorda.

### Sõnumimaakler

Tootja ja tarbija ei pruugi töötada samal ajal. Seetõttu on vaja vahekihti, mis võtab töö vastu ja hoiab seda ootel.

Sõnumimaakler on vaheteenus, mis võtab sõnumi või tööülesande vastu ja annab selle tarbijale edasi.

Näide:

Selles praktikumis on `redis` Celery maakler. Publisher saadab tööülesande Redisesse. Worker võtab selle sealt töötlemiseks. Redis hoiab seda järjekorda mälus; sündmuse püsivam õppelogi on PostgreSQL-is.

### Worker

Kui töö on järjekorras, peab eraldi protsess selle päriselt ära tegema.

Worker on taustaprotsess, mis võtab tööülesande ja täidab selle.

Näide:

Selles praktikumis võtab `worker` konteiner ühe müügisündmuse `event_id`, loeb sündmuse tabelist `stream.event_log` ja uuendab tabeleid `analytics.order_events` ning `analytics.sales_summary_live`.

### Järjekorrapõhine ja logipõhine maakler

Maaklerid erinevad selle poolest, kas sõnum kaob pärast töötlemist või jääb loetavasse logisse alles.

Järjekorrapõhises süsteemis võtab worker sõnumi tööks ja kinnitab selle. Pärast edukat kinnitust ei ole sõnum tavaliselt enam järjekorras.

Logipõhises süsteemis jääb sõnum alles. Tarbija peab ise meeles, millise kohani ta on lugenud.

Näide:

Redis + Celery on siin järjekorrapõhine. Apache Kafka on logipõhine. PostgreSQL-i tabel `stream.event_log` aitab meil sündmuseid õppekeskkonnas alles hoida ja `SQL`-iga uurida.

### Kinnitus ehk `ack`

Maakler peab teadma, kas worker jõudis tööülesande päriselt käsitleda. Ainult töö vastuvõtmisest ei piisa.

Kinnitus ehk `ack` (`acknowledgement`) on signaal, millega worker ütleb maaklerile, et tööülesanne on vastu võetud või töödeldud.

Näide:

Kui worker töötleb müügisündmuse edukalt, kinnitab Celery tööülesande. Kui töö katkeb enne kinnitust, võib sama tööülesanne hiljem uuesti tulla.

### Idempotentsus

Taustatöö võib tõrke või korduskatse tõttu sama sündmust uuesti näha.

Idempotentsus tähendab, et sama sündmuse korduv töötlemine ei muuda lõpptulemust topelt.

Näide:

Kui sama `event_id` pannakse uuesti järjekorda, ei tohi `analytics.order_events` tabelisse tekkida teist sama rida. Selleks kasutame `event_id` põhist unikaalsust.

### Sündmuse aeg ja töötluse aeg

Reaalajalähedases süsteemis ei jõua sündmus alati töötlusse samal hetkel, kui see allikas juhtus.

Sündmuse aeg näitab, millal sündmus päriselt juhtus. Töötluse aeg näitab, millal töövoog selle ära töötles.

Näide:

Tellimus võib olla tehtud kell `12:04`, aga worker töötleb seda alles kell `12:08`.

Ajapõhised koondid peaksid tavaliselt kasutama sündmuse aega. Töötluse aeg on lihtsam, aga võib anda vale akna.

### Aken

Voog ei lõpe loomulikult ära nagu fail või päevapakk. Analüüsiks tuleb valida ajavahemik, mille kaupa sündmuseid koondame.

Aken piiritleb osa voost ajavahemiku järgi.

Näide:

5 minuti aken `12:00` kuni `12:05` sisaldab selle aja jooksul toimunud tellimusi.

Selles praktikumis ehitame lihtsa 5 minuti kattuvuseta akna.

### Vesimärk

Hilinenud sündmuste ootamine parandab koondi täpsust, aga lõputult oodates ei saa koond kunagi valmis.

Vesimärk on reegel või hinnang, mis ütleb, kui kaua hilinenud sündmuseid veel vastu võtame.

Näide:

Kui reegel ütleb, et üle 2 minuti hilinenud sündmus on hiline, märgime selle tabelisse `staging.late_events`.

Selles baastaseme praktikumis ei ehitata täismahus vesimärgi mootorit. Hilinemine tehakse lihtsalt nähtavaks.

## Soovitatud töötee

Põhirada tee ühes terminalis. Worker töötab taustal eraldi konteineris.

Kõik käsud käivita hosti terminalis kaustas `08-reaalajas-andmetootlus/baastase`.

## 1. Ava praktikumi kaust

Liigu õigesse kausta:

```bash
cd 08-reaalajas-andmetootlus/baastase
```

Kontrolli asukohta:

```bash
pwd
ls
```

Oodatav tulemus: näed faile `README.md`, `compose.yml`, `.env.example`, `Dockerfile.app` ja kaustu `scripts`, `init`, `source_data`.

## 2. Loo `.env` fail

Kopeeri näidisfail:

```bash
cp .env.example .env
```

`.env` failis on andmebaasi ja Celery ühenduse väärtused.

Selles praktikumis on need õppekeskkonna näidisväärtused. Päris töös ei panda paroole git ajalukku. Sellepärast on `.env` lisatud `.gitignore` faili.

## 3. Vaata üle teenused

Ava fail `compose.yml`.

Teenused on järgmised:

| Teenus | Mida teeb? | Miks seda vaja on? |
|---|---|---|
| `db` | PostgreSQL-i andmebaas | Hoiab sündmuste logi, worker'i logi ja analüütika tabeleid |
| `redis` | Redise server | Hoiab Celery tööülesandeid mälus olevas järjekorras |
| `app` | Pythoni käsukonteiner | Siit käivitad publisher'i ja SQL kontrollid |
| `worker` | Celery worker | Võtab Redisest tööülesandeid ja uuendab analüütika tabeleid |

Andmete liikumine on selline:

```text
webshop_demo.py
  -> stream.event_log
  -> Redise järjekord
  -> Celery worker
  -> analytics.order_events
  -> analytics.sales_summary_live
```

Oluline mõte:

Redise järjekord aitab worker'il töid saada. PostgreSQL-i tabel `stream.event_log` aitab sul näha, mis tegelikult juhtus.

## 4. Käivita keskkond

Käivita teenused:

```bash
docker compose up -d --build
```

Esimesel korral võib Docker tõmmata ja ehitada tõmmiseid. See võib võtta mõne minuti.

Kontrolli teenuseid:

```bash
docker compose ps
```

Oodatav tulemus: teenused `db`, `redis`, `app` ja `worker` on olekus `running` või `healthy`.

Kui `worker` ei ole kohe valmis, oota 10 kuni 20 sekundit ja käivita kontroll uuesti.

## 5. Kontrolli tühja algseisu

Käivita SQL kontroll:

```bash
docker compose exec app psql -f scripts/01_check_stream.sql
```

See käsk töötab `app` konteineris. `psql` ühendub sealt `db` konteineriga.

Oodatav tulemus:

- `stream.event_log` ei sisalda veel sündmuseid;
- `analytics.sales_summary_live` on tühi;
- `monitoring.worker_task_log` on tühi.

Kui näed vanu ridu, oled praktikumit varem käivitanud. Vaata juhendi lõpus jaotist [Koristamine](#koristamine).

## 6. Avalda veebipoe sündmused

Avalda 10 müügisündmust:

```bash
docker compose exec app python scripts/webshop_demo.py publish --count 10 --delay-seconds 0.2
```

See käsk teeb iga sündmuse jaoks kaks asja:

- kirjutab sündmuse tabelisse `stream.event_log`;
- saadab Celery tööülesande Redise järjekorda.

Ajatemplite juures tasub hoida eraldi kaht mõtet:

| Veerg | Mida see näitab? | Kust see väärtus tuleb? |
|---|---|---|
| `event_time` | Millal tellimus näite järgi veebipoes juhtus | Simuleeritud äriaeg, mille loob `webshop_demo.py` |
| `published_at` | Millal sündmus kirjutati tabelisse `stream.event_log` | PostgreSQL-i `now()` väärtus sisestamise hetkel |
| `queued_at` | Millal tööülesanne saadeti Celery järjekorda | `app` konteineri kell käsu käivitamise ajal |
| `processed_at` | Millal worker sündmuse töötles | `worker` konteineri kell töötluse ajal |

Seega `event_time` ei ole päris veebipoe süsteemist tulnud aeg. See on õppenäite jaoks simuleeritud. Teised ajatemplid tekivad töö käigus ja näitavad, millal sinu Docker Compose keskkond vastava sammu tegi.

Oodatav väljund sisaldab ridu kujul:

```text
Avaldatud event_id=... task_id=... order_id=...
Kokku avaldati 10 sündmust.
```

Kontrolli tulemust:

```bash
docker compose exec app psql -f scripts/01_check_stream.sql
```

Oodatav tulemus:

- `stream.event_log` sisaldab 10 sündmust;
- osa või kõik sündmused on olekus `processed`;
- `analytics.sales_summary_live` sisaldab müügikoondit poe ja toote kaupa.

Kui worker ei jõudnud veel kõike töödelda, oota paar sekundit ja käivita kontroll uuesti.

## 7. Vaata, mida worker tegi

Vaata worker'i logi:

```bash
docker compose logs worker --tail 40
```

Logis peaks olema näha, et worker sai Celery tööülesandeid ja töötles neid.

Kontrolli worker'i olekut SQL-iga:

```bash
docker compose exec app psql -f scripts/04_check_worker_state.sql
```

Oodatav tulemus:

- `stream.event_log` ridadel on olek `processed`;
- `monitoring.worker_task_log` sisaldab töötluskatseid;
- `analytics.sales_summary_live` on uuenenud.

## 8. Peata worker ja vaata järjekorda

See samm teeb nähtavaks, miks järjekorda vaja on.

Peata worker:

```bash
docker compose stop worker
```

Avalda 5 uut sündmust:

```bash
docker compose exec app python scripts/webshop_demo.py publish --count 5 --delay-seconds 0.2
```

Vaata Redise järjekorra ja andmebaasi olekut:

```bash
docker compose exec app python scripts/webshop_demo.py queue-status
docker compose exec app psql -f scripts/01_check_stream.sql
```

Oodatav tulemus:

- Redise järjekorras on tööülesandeid;
- osa sündmuseid on andmebaasis olekus `queued`;
- live-koond ehk jooksvalt uuenev koond ei ole nende uute sündmuste võrra veel uuenenud.

Käivita worker uuesti:

```bash
docker compose start worker
```

Oota mõni sekund ja kontrolli uuesti:

```bash
docker compose exec app python scripts/webshop_demo.py queue-status
docker compose exec app psql -f scripts/01_check_stream.sql
```

Oodatav tulemus: järjekord tühjeneb ja sündmused liiguvad olekusse `processed`.

Õpitav mõte:

Publisher ja worker on lahti seotud. Veebipood saab sündmuse avaldada ka siis, kui worker on ajutiselt peatatud.

## 9. Proovi kordustöötlust

Pane viimane sündmus uuesti järjekorda:

```bash
docker compose exec app python scripts/webshop_demo.py enqueue-duplicate --last-event
```

Oota paar sekundit ja kontrolli:

```bash
docker compose exec app psql -f scripts/04_check_worker_state.sql
docker compose exec app psql -f scripts/05_check_idempotency.sql
```

Oodatav tulemus:

- worker võib sama `event_id` uuesti näha;
- `stream.task_dispatch_log` võib näidata sama sündmuse kohta mitut järjekorda saatmist;
- `analytics.order_events` topeltridade kontroll ei tagasta ridu;
- `monitoring.worker_task_log` võib näidata korduva sündmuse juures olekut `skipped`.

Õpitav mõte:

Taustatöödes tuleb arvestada kordustega. Sama sündmuse korduv töötlus ei tohi lõpptulemust topelt muuta.

## 10. Võrdle sündmuse aega ja töötluse aega

Avalda üks hilinenud sündmus:

```bash
docker compose exec app python scripts/webshop_demo.py publish --scenario late-event
```

Kontrolli sündmuse ja töötluse aega:

```bash
docker compose exec app psql -f scripts/06_check_event_time.sql
```

Oodatav tulemus: vähemalt ühel real on `event_time` märgatavalt varasem kui `processed_at`.

Õpitav mõte:

Kui koondame andmeid ajaakendesse, peaksime tavaliselt kasutama sündmuse aega. Töötluse aeg võib olla hilisem ja nihutada sündmuse valesse aknasse.

## 11. Ehita ajakna koondid

Ehita 5 minuti akna koondid:

```bash
docker compose exec app psql -f scripts/02_build_time_windows.sql
```

Skript ehitab kaks koondit:

- `analytics.sales_windows_event_time` kasutab sündmuse aega;
- `analytics.sales_windows_processing_time` kasutab töötluse aega.

Oodatav tulemus: kui hilinenud sündmus on olemas, võivad need kaks koondit erineda.

Skript märgib üle 2 minuti hilinenud sündmused ka tabelisse `staging.late_events`.

See on lihtsustatud vesimärgi mõte. Siin ei ehitata täielikku voogtöötluse olekuhalduse mootorit.

## 12. Võrdle live-koondit pakktöötlusega

Ehita sama koond pakktöötlusena kogu töödeldud sündmuste tabeli põhjal:

```bash
docker compose exec app psql -f scripts/03_compare_batch_and_stream.sql
```

Oodatav tulemus: veerg `comparison_result` näitab `OK`.

Kui tulemus on `ERINEB`, on tavaliselt üks kahest probleemist:

- worker ei jõudnud veel kõiki sündmuseid töödelda;
- kordustöötluse idempotentsus ei töötanud.

Õpitav mõte:

Reaalajalähedane koond ja pakktöötluse koond võivad kasutada sama äriloogikat. Erinevus on selles, millal ja kuidas koond uueneb.

## 13. Proovi vigast sündmust

Avalda 5 sündmust nii, et viimane on vigane:

```bash
docker compose exec app python scripts/webshop_demo.py publish --count 5 --include-bad-event
```

Oota paar sekundit ja kontrolli:

```bash
docker compose exec app psql -f scripts/01_check_stream.sql
docker compose exec app psql -f scripts/07_check_bad_events.sql
```

Oodatav tulemus:

- korrektsed sündmused töödeldakse ära;
- vigane sündmus jõuab olekusse `failed`;
- vea põhjus on tabelis `staging.bad_events`.

Õpitav mõte:

Ühe vigase sündmuse tõttu ei tohiks kogu worker seisma jääda. Vigane sündmus tuleb nähtavaks teha ja ülejäänud töö peab jätkuma.

## 14. Seos edasijõudnute Kafka praktikumi teemaga

Selles baastaseme praktikumis kasutasime järjekorrapõhist lahendust:

- Redis hoiab tööülesandeid järjekorras;
- Celery worker võtab tööülesande ja kinnitab selle;
- PostgreSQL hoiab õppekeskkonna jaoks sündmuste logi ja analüütika tabeleid.

Edasijõudnute praktikumis kasutatakse Apache Kafka ja Apache Spark Structured Streaming lahendust.

Seal tulevad juurde:

- Kafka teema ehk `topic`;
- partitsioonid ehk teema väiksemad osad;
- offsetid ehk lugemiskohad logis;
- tarbijagrupid;
- Apache Spark Structured Streaming;
- sündmuse aja põhised aknad ja vesimärgid päris voogtöötluse raamistikus;
- Delta tabelid ja checkpoint'id ehk kontrollpunktid.

Selle praktikumi mõte on anda neile teemadele alus ilma, et peaks kohe Kafkat ja Sparki käivitama.

## Kontrollpunktid

| Kontrollpunkt | Oodatav tulemus |
|---|---|
| Teenused töötavad | `docker compose ps` näitab teenuseid `db`, `redis`, `app`, `worker` |
| Sündmused on avaldatud | `stream.event_log` sisaldab ridu |
| Worker töötas | `monitoring.worker_task_log` sisaldab töötluskatseid |
| Live-koond uuenes | `analytics.sales_summary_live` sisaldab müügikoondit |
| Worker'i peatamine töötab | uued sündmused jäävad alguses olekusse `queued` |
| Worker'i taaskäivitamine töötab | järjekord tühjeneb ja sündmused liiguvad olekusse `processed` |
| Kordustöötlus on ohutu | sama `event_id` ei tekita topeltrida |
| Hilinenud sündmus on nähtav | `staging.late_events` sisaldab hilinemise infot |
| Pakktöötlus ja live-koond klapivad | `comparison_result` on `OK` |
| Vigane sündmus on kontrollitav | `staging.bad_events` sisaldab vea põhjust |

## Levinud vead ja lahendused

| Sümptom | Tõenäoline põhjus | Lahendus |
|---|---|---|
| `docker compose` ei leia faili | Oled vales kaustas | Käivita `pwd` ja liigu kausta `08-reaalajas-andmetootlus/baastase` |
| `port is already allocated` | Port `5438` on kasutusel | Muuda `.env` failis `DB_PORT_HOST` väärtust või peata teine teenus |
| `worker` ei töötle sündmuseid | Worker on peatatud või käivitub alles | Kontrolli `docker compose ps` ja `docker compose logs worker --tail 40` |
| `publish` käsk katkeb Redise ühenduse veaga | `redis` konteiner ei tööta või pole veel valmis | Kontrolli `docker compose ps`, käivita vajadusel `docker compose start redis` ja proovi avaldamist uuesti |
| Redise järjekord ei tühjene | Worker ei saa Redise või andmebaasiga ühendust | Vaata `docker compose logs worker` ja kontrolli `.env` väärtuseid |
| `relation does not exist` | Andmebaasi init-skript ei jooksnud või kasutad vana mahtu | Käivita `docker compose down -v` ja seejärel `docker compose up -d --build` |
| Live-koond ja pakktöötlus erinevad | Kõik tööülesanded pole veel töödeldud | Oota mõni sekund ja käivita kontroll uuesti |
| Topeltread tekivad | Idempotentsuse kaitse puudub või on katki | Kontrolli, et `analytics.order_events.event_id` on primaarvõti |
| Ajaakna koond tundub vale | Kasutasid töötluse aega, mitte sündmuse aega | Võrdle tabeleid `sales_windows_event_time` ja `sales_windows_processing_time` |
| Vigane sündmus ei ilmu koondisse | See on oodatav | Vaata vea põhjust tabelist `staging.bad_events` |

## Kokkuvõte

Selles praktikumis tegid läbi väikese reaalajalähedase töövoo:

- avaldasid veebipoe müügisündmuseid;
- saatsid iga sündmuse kohta Celery tööülesande Redise järjekorda;
- lasid worker'il sündmused analüütika tabelitesse töödelda;
- kontrollisid töötluse olekut SQL-iga;
- peatasid worker'i ja nägid, kuidas järjekord töid hoiab;
- proovisid kordustöötlust ja idempotentsust;
- võrdlesid sündmuse aega ja töötluse aega;
- ehitasid lihtsad ajakna koondid;
- võrdlesid live-koondit pakktöötlusega.

Peamine mõte: reaalajalähedane töötlus ei tähenda ainult kiiret käsku. Vaja on maaklerit, nähtavat olekut, vigade käsitlemist, idempotentsust ja selget arusaama ajast.

Seda mustrit saab kasutada ka ajakriitilise ja mitteajakriitilise töö eraldamiseks. Veebipoes peab ostu kinnitamine olema otse ja kiire. Kõrvaltegevused, näiteks analüütika koondi uuendamine, teavituse saatmine või riskikontrolli lisasamm, võivad käia ostu lähedal, aga eraldi taustatööna. Nii ei pea kasutaja ootama, kuni kõik seotud protsessid lõpuni jõuavad.

Pakktöötlus ja järjekorrapõhine töötlus sobivad eri olukordadesse. Pakktöötlus sobib siis, kui andmeid on mõistlik töödelda korraga: näiteks päeva lõpu raport, ajaloolise andmestiku parandamine või kogu koondi uuesti arvutamine. Järjekorrapõhine töötlus sobib siis, kui iga sündmus peaks jõudma edasi võimalikult kiiresti, kuid mitte tingimata samas protsessis: näiteks müügisündmuse analüütikasse saatmine, teavituse koostamine või mahukam lisakontroll.

## Valikulised lisaharjutused

### Lisaülesanne 1: jälgi worker'it teises terminalis

Ava teine terminal samas kaustas ja käivita:

```bash
docker compose logs -f worker
```

Esimeses terminalis avalda sündmuseid:

```bash
docker compose exec app python scripts/webshop_demo.py publish --count 5 --delay-seconds 1
```

Vaata, kuidas worker'i logi uueneb.

### Lisaülesanne 2: lisa suurte tellimuste hoiatus

Muuda worker'i loogikat nii, et üle 100 euro suurused tellimused kirjutatakse uude tabelisse `analytics.large_order_alerts`.

Mõtle enne:

- milline veerg näitab tellimuse kogusummat;
- kas hoiatus peab olema idempotentne;
- kas sama `event_id` võib hoiatuse tabelisse sattuda mitu korda.

### Lisaülesanne 3: lisa uus sündmusetüüp `order_cancelled`

Praegu töötleb worker ainult sündmuseid `order_created`.

Mõtle, kuidas peaks käituma tühistamise sündmus:

- kas see vähendab live-koondit;
- kas algne tellimus peab olemas olema;
- kas tühistamine peaks olema eraldi faktitabelis.

Kirjuta oma lahendus lühikese plaanina või proovi seda koodis.

### Lisaülesanne 4: avasta edasijõudnute rada

Ava [edasijõudnute praktikum](../edasijoudnud/README.md).

Ära püüa kogu juhendit korraga lõpuni läbi teha. Loe seda pigem nagu järgmist sammu samal teemal.

Pane tähele:

- kus Redise järjekorra asemel tuleb mängu Kafka teema ehk `topic`;
- kuidas `partition` ja `offset` aitavad sündmuste lugemist jälgida;
- kus Spark Structured Streaming kasutab sündmuse aega, aknaid ja vesimärke;
- miks `checkpoint` ehk kontrollpunkt on vajalik, kui töötlus peab jätkuma pärast katkestust.

Kui mõni mõiste tundub juba tuttav, siis on see hea märk: baastaseme praktikum valmistas selleks ette. Kui mõni mõiste jääb veel häguseks, pane see endale lihtsalt hilisemaks küsimuseks kirja.

## Koristamine

Kui tahad tühjendada ainult Redise järjekorra ja PostgreSQL-i tabelid, käivita:

```bash
docker compose exec app python scripts/webshop_demo.py clear-queue
docker compose exec app psql -f scripts/99_reset.sql
```

Kui tahad peatada teenused ja kustutada ka andmebaasi mahu, käivita:

```bash
docker compose down -v
```

Järgmisel käivitamisel luuakse andmebaasi tabelid uuesti.
