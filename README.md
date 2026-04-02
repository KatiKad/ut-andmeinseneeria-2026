# Andmeinseneride täiendkoolitusprogramm — Praktikumid

Tartu Ülikooli andmeinseneride täiendkoolitusprogrammi praktikumimaterjalid.
Programm koosneb 13 nädalast: 9 sisumoodulit ja 4 nädalat projektitööd ning kaitsmist.
Iga sisumooduli praktikum pakub kahte rada:

- **Baastase** — samm-sammult juhendatud, sobib teemaga alles tutvujale
- **Edasijõudnud** — kiirem tempo ja suurem iseseisvus, eeldab varasemat kogemust

## Viited

- [Andmeinseneride täiendkoolitusprogramm](https://koolitus.edu.ee/training/19668) — täpsem koolituse info täiendkoolituste infosüsteemis
- [Moodle](https://moodle.ut.ee/course/view.php?id=14750) — materjalid, tagasiside, lingid
- [Tööriistade paigaldus](./common-setup/README.md) — Docker ja muu seadistus

## Nädalate ülevaade

### [01 — Andmeinseneeria alused](./01-andmeinseneeria-alused/)

Sissejuhatus andmeinseneeriasse: Docker, PostgreSQL, CSV laadimine, esimene andmetöövoo harjutus.

- [Baastase](./01-andmeinseneeria-alused/baastase/README.md): PostgreSQL ühendus, CSV laadimine, töövoo põhiloogika
- [Edasijõudnud](./01-andmeinseneeria-alused/edasijoudnud/README.md): Python ETL, REST API, andmete normaliseerimine, idempotentsus

### [02 — Andmemudelid](./02-andmemudelid-ja-baasid/)

Relatsiooniline ja dimensionaalne modelleerimine. Star schema kavandamine ja ehitamine.

- [Baastase](./02-andmemudelid-ja-baasid/baastase/README.md): tähtskeemi loomine, faktitabel ja dimensioonid, SQL joinid ja agregatsioonid
- [Edasijõudnud](./02-andmemudelid-ja-baasid/edasijoudnud/README.md): Kimballi metoodika, SCD Type 2, päringu jõudluse analüüs

### [03 — Andmete integreerimine](./03-andmete-integreerimine/)

Andmete kogumine failidest ja API-dest, puhastamine ja laadimine. Transformatsioonitööriistad (dbt).

- [Baastase](./03-andmete-integreerimine/baastase/README.md): CSV/Parquet/API allikast laadimine, andmete puhastamine, ETL etapid
- [Edasijõudnud](./03-andmete-integreerimine/edasijoudnud/README.md): inkrementaalne laadimine, idempotentsus, logitud ja veahaldusega ETL

### [04 — Andmetorude orkestreerimine](./04-andmetorude-orkestreerimine/)

Andmetorustiku automatiseerimine: ajastamine, sõltuvused, orkestreerimise põhimõtted.

- [Baastase](./04-andmetorude-orkestreerimine/baastase/README.md): CRON ajastus, logide kogumine, sõltuvuste ja retry põhimõtted
- [Edasijõudnud](./04-andmetorude-orkestreerimine/edasijoudnud/README.md): Airflow DAG, operaatorid, sõltuvused, backfill

### [05 — Suurandmed ja pilvelahendused](./05-suurandmed-ja-pilvelahendused/)

Suurandmete põhimõtted, pilve kasutusloogika, kaasaegsed andmeformaadid.

- [Baastase](./05-suurandmed-ja-pilvelahendused/baastase/README.md): Parquet, avatud tabeliformaadid, hajussüsteemid, Databricks sissejuhatus
- [Edasijõudnud](./05-suurandmed-ja-pilvelahendused/edasijoudnud/README.md): Spark DataFrame transformatsioonid, partitsioneerimine, data lakehouse

### [06 — Andmekvaliteet ja andmehaldus](./06-andmekvaliteet-ja-haldus/)

Kvaliteedikontrollid andmetöövoogudes: dokumenteerimine ja metaandmete haldamine.

- [Baastase](./06-andmekvaliteet-ja-haldus/baastase/README.md): kvaliteedireeglid, vigaste ridade tuvastamine, andmekataloogide väärtus
- [Edasijõudnud](./06-andmekvaliteet-ja-haldus/edasijoudnud/README.md): automatiseeritud testid, kvaliteediraport, data lineage, andmekataloogi roll

### [07 — Andmeturve ja privaatsus](./07-andmeturve-ja-privaatsus/)

Ligipääsud, rollid ja tundlike andmete käsitlemine: minimaalõiguste printsiip.

- [Baastase](./07-andmeturve-ja-privaatsus/baastase/README.md): PII, rollipõhine ligipääs, saladuste turvaline hoidmine
- [Edasijõudnud](./07-andmeturve-ja-privaatsus/edasijoudnud/README.md): andmete maskeerimine, audit logid, GDPR, row-level security

### [08 — Reaalajas andmetöötlus](./08-reaalajas-andmetootlus/)

Sündmuspõhine arhitektuur ja voogandmete töötlemine.

- [Baastase](./08-reaalajas-andmetootlus/baastase/README.md): sündmused, publish/subscribe simulatsioon, batch vs streaming
- [Edasijõudnud](./08-reaalajas-andmetootlus/edasijoudnud/README.md): Apache Kafka, topic/partition/consumer group, voogandmete transformatsioonid

### [09 — Ärianalüütika ja andmete serveerimine](./09-arianalyytika-ja-serveerimine/)

Tehniline töö seotud äriväärtusega: dashboardid, KPI-d, andmepõhine lugu.

- [Baastase](./09-arianalyytika-ja-serveerimine/baastase/README.md): lihtne dashboard, KPI-de selgitamine, andmetest järelduste tegemine
- [Edasijõudnud](./09-arianalyytika-ja-serveerimine/edasijoudnud/README.md): esitlusvalmis demo, mõõdikute definitsioonid, seos kvaliteedi ja turvalisusega