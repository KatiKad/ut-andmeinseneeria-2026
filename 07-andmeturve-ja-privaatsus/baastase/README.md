# Praktikum 7: Andmeturve ja privaatsus (baastase)

## Sisukord

- [Praktikumi eesmärk](#praktikumi-eesmärk)
- [Õpiväljundid](#õpiväljundid)
- [Hinnanguline ajakulu](#hinnanguline-ajakulu)
- [Eeldused](#eeldused)
- [Enne alustamist](#enne-alustamist)
- [Praktikumi failid](#praktikumi-failid)
- [Miks see teema on oluline?](#miks-see-teema-on-oluline)
- [Uued mõisted](#uued-mõisted)
- [Soovitatud töötee](#soovitatud-töötee)
- [1. Ava õige kaust](#1-ava-õige-kaust)
- [2. Vaata üle praktikumi failid](#2-vaata-üle-praktikumi-failid)
- [3. Loo `.env` fail ja kontrolli `.gitignore` reeglit](#3-loo-env-fail-ja-kontrolli-gitignore-reeglit)
- [4. Käivita konteinerid](#4-käivita-konteinerid)
- [5. Loo skeemid ja toortabel](#5-loo-skeemid-ja-toortabel)
- [6. Laadi sünteetilised osalejaandmed](#6-laadi-sünteetilised-osalejaandmed)
- [7. Koosta PII register](#7-koosta-pii-register)
- [8. Loo rollid, vaated ja õigused](#8-loo-rollid-vaated-ja-õigused)
- [9. Kontrolli rolle ühe skriptiga](#9-kontrolli-rolle-ühe-skriptiga)
- [10. Proovi keelatud päringut](#10-proovi-keelatud-päringut)
- [11. Tee õiguste kokkuvõte](#11-tee-õiguste-kokkuvõte)
- [Kontrollpunktid](#kontrollpunktid)
- [Levinud vead ja lahendused](#levinud-vead-ja-lahendused)
- [Kokkuvõte](#kokkuvõte)
- [Valikuline lisaharjutus](#valikuline-lisaharjutus)
- [Koristamine](#koristamine)

## Praktikumi eesmärk

Selle praktikumi eesmärk on harjutada tundlike andmete turvalist käsitlemist väikeses PostgreSQL-i andmebaasis.

Praktikumi lõpuks näed läbi ühe lihtsa, aga tööelus väga tavalise olukorra:

- ühes toortabelis on nii analüüsiks vajalikud väljad kui ka isikuandmed;
- kõik rollid ei tohi näha samu veerge ega samu andmekihte;
- saladused, näiteks andmebaasi parool, ei kuulu git ajalukku;
- andmebaasi õigused peavad järgima minimaalõiguste põhimõtet.

See praktikum ei ole õigusnõu. Keskendume tehnilisele poolele: kuidas andmeinsener saab andmestiku, rollid ja ligipääsud arusaadavalt ning kontrollitavalt üles seada.

## Õpiväljundid

Praktikumi lõpuks oskad:

- selgitada, mida tähendab `PII` ehk isikut tuvastada võimaldav teave;
- eristada otsest PII-d, kaudset PII-d ja mitte-PII välju;
- hoida andmebaasi parooli `.env` failis nii, et see ei jõuaks git ajalukku;
- luua lihtsad PostgreSQL rollid;
- anda rollidele ligipääsu vaadetele, mitte otse toortabelile;
- kontrollida `SET ROLE` abil, mida eri rollid näevad;
- tõlgendada `permission denied` veateadet turvakontrolli osana.

## Hinnanguline ajakulu

Arvesta umbes 2 tunniga.

See aeg jaguneb ligikaudu nii:

- 20 min keskkonna ja failidega tutvumiseks;
- 15 min `.env` ja `.gitignore` kontrolliks;
- 20 min andmebaasi, skeemide ja toortabeli loomiseks;
- 25 min PII registri ja tundlike väljade aruteluks;
- 30 min rollide, vaadete ja õiguste kontrolliks;
- 10 min kokkuvõtteks ja lisaülesande alustamiseks.

## Eeldused

Sul on vaja:

- `VS Code`-i või GitHub Codespacesit;
- terminali;
- töötavat Dockeri keskkonda;
- selle repositooriumi faile.

Kasuks tuleb, kui eelmiste baastaseme praktikumide põhjal on tuttavad järgmised töövõtted:

- oskad avada õige praktikumi kausta;
- oskad luua `.env` faili `.env.example` põhjal;
- oskad käivitada käsu `docker compose up -d`;
- oskad avada `psql` kliendi käsuga `docker compose exec client psql`;
- tead, et osa käske käib hosti terminalis ja osa käske käib `psql` sees.

Kui mõni neist sammudest on veel ebakindel, vaata vajadusel üle:

- [Praktikum 1: PostgreSQL-iga ühenduse loomine ja esimese CSV-faili laadimine](../../01-andmeinseneeria-alused/baastase/README.md)
- [Praktikum 2: Lihtne faktitabel ja kaks dimensiooni](../../02-andmemudelid-ja-baasid/baastase/README.md)
- [Praktikum 3: Andmete integreerimine API ja CSV abil](../../03-andmete-integreerimine/baastase/README.md)

## Enne alustamist

### Soovitatud keskkond

Selle praktikumi jaoks sobib hästi järgmine tööviis:

- ava kaust `07-andmeturve-ja-privaatsus/baastase` `VS Code`-is;
- kasuta `VS Code`-i sisseehitatud terminali;
- hoia korraga lahti `README.md`, `compose.yml` ja `scripts/04_create_roles_and_views.sql`;
- käivita käsud hosti terminalist, kui juhendis ei ole öeldud teisiti.

Host tähendab sinu arvutit või Codespace'i tööruumi. Konteiner tähendab Dockeri sees töötavat teenust.

Selles praktikumis on kaks konteinerit:

- `db` on PostgreSQL andmebaas;
- `client` on käsurea konteiner, kust käivitad `psql` käsud.

Kui käsus on `docker compose exec client psql`, siis käivitatakse `psql` `client` konteineris. `db` konteiner hoiab ainult andmebaasi.

Kui töötad GitHub Codespacesis, siis on praktikumi kaust tavaliselt siin:

```text
/workspaces/ut-andmeinseneeria-2026/07-andmeturve-ja-privaatsus/baastase
```

### Puhas algus

See praktikum kasutab hosti porti `5437`.

Kui see port on mõne muu teenuse poolt hõivatud, muuda failis `.env` väärtust `DB_PORT_HOST` või peata konfliktne teenus.

Kui oled seda praktikumi varem käivitanud ja tahad täiesti puhast andmebaasi, kasuta juhendi lõpus käsku:

```bash
docker compose down -v
```

See kustutab ka Dockeri andmemahu. Järgmisel käivitamisel luuakse andmebaas uuesti.

## Praktikumi failid

Kõik allpool toodud suhtelised failiteed eeldavad, et asud kaustas `07-andmeturve-ja-privaatsus/baastase`.

- [`compose.yml`](./compose.yml) kirjeldab PostgreSQL andmebaasi ja `psql` kliendi konteinerit
- [`.env.example`](./.env.example) sisaldab näidisväärtusi andmebaasi kasutaja, parooli ja pordi jaoks
- [`.gitignore`](./.gitignore) ütleb gitile, et `.env` faili ei jälgita
- [`data/osalejad.csv`](./data/osalejad.csv) sisaldab väljamõeldud osalejaandmeid
- [`scripts/01_create_objects.sql`](./scripts/01_create_objects.sql) loob skeemid ja toortabeli
- [`scripts/02_load_data.sql`](./scripts/02_load_data.sql) laadib `CSV` faili toortabelisse
- [`scripts/03_create_pii_register.sql`](./scripts/03_create_pii_register.sql) loob PII registri
- [`scripts/04_create_roles_and_views.sql`](./scripts/04_create_roles_and_views.sql) loob rollid, maskeeritud vaated ja õigused
- [`scripts/05_check_results.sql`](./scripts/05_check_results.sql) kontrollib ridade arvu, rolle ja nähtavaid andmeid
- [`scripts/99_reset.sql`](./scripts/99_reset.sql) eemaldab praktikumi skeemid ja rollid

Käsud kasutavad suhtelisi teid, näiteks `scripts/02_load_data.sql` ja `data/osalejad.csv`. Nii töötavad samad käsud macOS-is, Linuxis, Git Bashis, Windows PowerShellis ja GitHub Codespacesis.

Andmefaili laadimisel kasutab skript `\copy` käsku. See tähendab, et `data/osalejad.csv` loetakse kliendi konteinerist ja saadetakse sealt andmebaasi.

## Miks see teema on oluline?

Andmeinseneri töö ei lõpe sellega, et andmed jõuavad tabelisse.

Sageli on vaja vastata ka järgmistele küsimustele:

- kas tabelis on isikuandmeid;
- millised veerud on kõige tundlikumad;
- kes tohib näha toorandmeid;
- kes tohib näha ainult maskeeritud andmeid;
- kas paroolid ja võtmed on kogemata git ajalukku sattunud;
- kas kasutajale on antud rohkem õigusi, kui tema töö vajab.

Kui samas tabelis on nimi, e-post, telefon, kursus ja staatus, siis ei ole see lihtsalt tehniline tabel. See on andmestik, millele ligipääs peab olema põhjendatud.

Selles praktikumis teeme selle põhimõtte nähtavaks kolme rolliga:

- `analyytik` näeb maskeeritud reataseme andmeid;
- `aruandlus` näeb ainult koondandmeid;
- `auditor` näeb toorandmeid ja turvatud vaateid.

## Uued mõisted

### PII

Probleem on selles, et mõni andmeväli võib inimest tuvastada.

`PII` tähendab inglise keeles `Personally Identifiable Information`. Eesti keeles kasutame siin selgitust: isikut tuvastada võimaldav teave.

Näide:

- e-posti aadress `maarja.kask@example.test` võib inimest otse tuvastada;
- linn üksi ei pruugi inimest tuvastada, aga koos kursuse, staatuse ja kuupäevaga võib risk suureneda.

Tehniliselt ei ole PII ainult üks kindel veergude nimekiri. Oluline on ka kontekst: kui palju andmeid on koos ja kes neid näeb.

### Otsene PII

Otsene PII on teave, mis võib inimese üsna otse tuvastada.

Näited:

- eesnimi ja perenimi;
- e-posti aadress;
- telefoninumber.

Selles praktikumis maskeerime need väljad analyytiku vaates.

### Kaudne PII

Kaudne PII ei pruugi üksi inimest tuvastada, kuid võib seda teha koos teiste väljadega.

Näited:

- linn;
- maakond;
- registreerumise kuupäev;
- sisemine osaleja tunnus.

Kaudne PII ei tähenda, et välja ei tohi kunagi kasutada. See tähendab, et pead mõtlema, kellele ja milleks seda näitad.

### RBAC

Probleem on selles, et iga kasutaja ei vaja samu õigusi.

`RBAC` tähendab inglise keeles `Role-Based Access Control`. Eesti keeles: rollipõhine ligipääsukontroll.

Näide:

- `analyytik` vajab andmeid mustrite uurimiseks;
- `aruandlus` vajab ainult koondtulemusi;
- `auditor` vajab kontrolli jaoks täielikku lugemisõigust.

Tehniliselt loome PostgreSQL rollid ja anname igale rollile `SELECT` õiguse ainult neile objektidele, mida ta vajab.

### Minimaalõigused

Minimaalõiguste põhimõte tähendab, et roll saab ainult need õigused, mida tal tööks vaja on.

Näide:

Kui aruandluse roll vajab osalejate arvu kursuse ja maakonna lõikes, siis ta ei vaja e-posti aadresse ega telefoninumbreid.

Selles praktikumis ei saa `aruandlus` roll ligipääsu toortabelile. Andmete vaatamiseks saab ta lugeda ainult koondvaadet.

### Vaikeroll ja õiguste jagamine

Selles õppekeskkonnas on andmebaasi vaikeroll `praktikum`. See tuleb `.env` failist:

```text
POSTGRES_USER=praktikum
```

Kui käivitad käsu `docker compose exec client psql ...` ja ei kasuta `SET ROLE` käsku, siis töötad `praktikum` kasutajana. See on õppekeskkonna administraatoriroll: ta loob selles praktikumis skeemid, tabelid, vaated ja rollid ning jagab teistele rollidele õigused. See ei ole näide tavakasutaja õigustest.

Rollid `analyytik`, `aruandlus` ja `auditor` on töörollid. Need ei ole eraldi sisselogimiskasutajad. Praktikumis võtad nende rollide vaate ajutiselt käsuga `SET ROLE`, et kontrollida, mida iga roll näeb. Seda saab teha, sest `praktikum` on õppekeskkonna seadistusroll.

Päris tööelus ei jaga kasutaja endale ise õigusi. Täpsed rollinimed erinevad, kuid vastutus jaguneb tavaliselt nii:

- andmeomanik otsustab, kellel on tööks ligipääsu vaja;
- andmekaitse või turbe eest vastutav roll aitab hinnata tundlike andmete riske;
- andmebaasi või andmeplatvormi administraator rakendab õigused tehniliselt;
- muudatused tehakse taotluse, kinnituse ja hilisema ülevaatuse kaudu.

Andmeinsener võib õiguste seadistuse valmis kirjutada, kuid laia ligipääsu otsus peab olema põhjendatud ja kontrollitav.

### Saladus

Saladus on väärtus, mida ei tohi avalikult git ajaloos hoida.

Näited:

- andmebaasi parool;
- `API` võti;
- privaatvõti;
- teenuse ligipääsumärgis.

Selles praktikumis on parool õppekeskkonna näidisväärtus, kuid töövõte on sama: parool on `.env` failis, mitte koodis.

### `.env`

`.env` on tekstifail, kus hoitakse keskkonnamuutujaid.

Probleem, mida `.env` lahendab: sama kood saab töötada eri keskkondades eri paroolide, portide ja andmebaasinimedega.

Näide:

```text
POSTGRES_USER=praktikum
POSTGRES_PASSWORD=praktikum
POSTGRES_DB=praktikum
DB_PORT_HOST=5437
```

Päris tööelus peab tootmise parool olema tugev ja git ajaloost väljas.

### `.gitignore`

`.gitignore` ütleb gitile, milliseid faile ei jälgita.

Probleem, mida `.gitignore` lahendab: arendaja võib vajada kohalikku `.env` faili, aga seda ei tohi kogemata git ajalukku lisada.

Selles praktikumis sisaldab `.gitignore` rida:

```text
.env
```

### Vaade ja maskeerimine

Vaade on salvestatud päring, mida saab kasutada nagu tabelit.

Probleem, mida vaade lahendab: toortabeli saab peita ja rollile saab näidata ainult sobivat kuju samadest andmetest.

Maskeerimine tähendab, et tundlik väärtus asendatakse osaliselt varjatud kujuga.

Näide:

```text
maarja.kask.naidis@example.test -> m***@example.test
```

### Anonüümimine ja pseudonüümimine

Maskeerimine ei ole sama mis anonüümimine.

Anonüümimise eesmärk on muuta andmed selliseks, et inimest ei saa enam mõistliku pingutusega tuvastada. See on tugev väide ja sõltub alati sellest, milliseid muid andmeid võib kõrval olla.

Pseudonüümimine tähendab, et otsene tunnus asendatakse teise tunnusega.

Näide:

```text
maarja.kask.naidis@example.test -> osaleja_1001
```

Kui kusagil on alles tabel, mis seob `osaleja_1001` tagasi e-posti aadressiga, siis ei ole andmed täielikult anonüümsed. Need on pseudonüümitud. Pseudonüümimine vähendab riski, aga võti-väärtus seost tuleb kaitsta nagu tundlikku infot.

### k-anonüümsus

Probleem tekib ka siis, kui nimi ja e-post on eemaldatud, aga alles jääb haruldane tunnuste kombinatsioon.

Näide:

Kui andmestikus on ainult üks inimene kombinatsiooniga `linn = Jõhvi`, `kursus = Andmeturve`, `staatus = aktiivne`, siis võib see rida olla äratuntav ka ilma nimeta.

`k-anonüümsus` tähendab, et iga valitud tunnuste kombinatsioon peab esinema vähemalt `k` real. Kui `k = 3`, siis ei tohiks ükski linn + kursus + staatus kombinatsioon olla seotud ainult ühe või kahe kirjega.

Selle saavutamiseks kasutatakse tavaliselt üldistamist või peitmist:

- linna asemel näidatakse maakonda;
- täpse kuupäeva asemel näidatakse kuud;
- liiga väiksed rühmad jäetakse koondist välja.

Selles praktikumis k-anonüümsust eraldi ei rakendata. Mõte aitab siiski hinnata, kas koondvaade on piisavalt üldine või kas mõni rühm on liiga väike.

### PII register, andmekataloog ja andmetöötlusregister

Selles praktikumis loodav `governance.pii_register` ei ole kogu andmekataloog ega andmetöötlusregister.

See on väike tehniline tabel, kus märgid toortabeli veergude kohta:

- kas veerg on otsene PII, kaudne PII või mitte-PII;
- miks see otsus tehti;
- kuidas veergu võiks vaadetes käsitleda.

Andmekataloog on laiem tööriist või süsteem. Seal hoitakse tavaliselt tabelite kirjeldusi, omanikke, ärimõisteid, silte, kvaliteediinfot ning infot andmete päritolu ja liikumise kohta.

Andmetöötlusregister ehk töötlemistoimingute register on teine asi. See kirjeldab andmetöötluse tegevusi, näiteks töötlemise eesmärki, vastutajaid, andmesubjekte, säilitust ja jagamist. Selles praktikumis seda juriidilist vaadet ei koostata.

Praktikas hoitakse PII klassifikatsiooni sageli andmekataloogis. Üks hea tööriist, mida edasi uurida, on [`OpenMetadata`](https://docs.open-metadata.org/latest/how-to-guides/data-governance/classification/overview). Seal saab andmeobjektidele lisada kirjeldusi, omanikke, termineid, silte ja klassifikatsioone. Sama ülesannet võivad täita ka `DataHub`, `Microsoft Purview`, `Collibra`, `Alation` või pilveplatvormi enda kataloogiteenus.

## Soovitatud töötee

Tee praktikum läbi selles järjekorras:

1. käivita konteinerid;
2. kontrolli andmebaasi ühendust;
3. loo toortabel ja laadi andmed;
4. märgi PII veerud registris;
5. loo rollid ja vaated;
6. kontrolli iga rolli vaadet;
7. proovi üht keelatud päringut.

Ära alusta rollide loomisest enne andmete laadimist. Vaated sõltuvad toortabelist.

## 1. Ava õige kaust

See samm tehakse hosti terminalis.

Kui alustad repo juurkaustast, liigu praktikumi kausta:

```bash
cd 07-andmeturve-ja-privaatsus/baastase
```

Kontrolli, et oled õiges kaustas.

macOS-is, Linuxis ja Codespacesis:

```bash
pwd
```

Windows PowerShellis:

```powershell
Get-Location
```

Oodatav tulemus: tee lõpus on `07-andmeturve-ja-privaatsus/baastase`.

## 2. Vaata üle praktikumi failid

See samm tehakse hosti terminalis.

Vaata, millised failid selles kaustas on:

```bash
ls
```

Kui kasutad PowerShelli, töötab sama käsk tavaliselt samuti. Võid kasutada ka:

```powershell
Get-ChildItem
```

Oluline on näha vähemalt neid:

```text
README.md
compose.yml
data
scripts
```

Vaata korraks ka skriptide nimekirja:

```bash
ls scripts
```

Oodatav tulemus: näed skripte `01_create_objects.sql` kuni `05_check_results.sql` ja `99_reset.sql`.

## 3. Loo `.env` fail ja kontrolli `.gitignore` reeglit

See samm tehakse hosti terminalis.

Loo `.env` fail näidisfaili põhjal.

macOS-is, Linuxis ja Codespacesis:

```bash
cp .env.example .env
```

Windows PowerShellis:

```powershell
Copy-Item .env.example .env
```

`.env` fail sisaldab andmebaasi kasutajat, parooli, andmebaasi nime ja hosti porti. Selles praktikumis on väärtused õppekeskkonna jaoks lihtsad.

Kontrolli, et git ignoreerib `.env` faili:

```bash
git check-ignore -v .env
```

Oodatav tulemus on midagi sarnast:

```text
.gitignore:1:.env	.env
```

Kui käsk ei väljasta midagi, siis git ei ignoreeri `.env` faili. Kontrolli, et failis `.gitignore` oleks rida `.env`.

## 4. Käivita konteinerid

See samm tehakse hosti terminalis.

Käivita andmebaasi ja kliendi konteinerid:

```bash
docker compose up -d
```

Käsk teeb kaks asja:

- loeb seadistuse failist `compose.yml`;
- käivitab andmebaasi ja `psql` kliendi konteineri taustal.

Kontrolli konteinerite seisu:

```bash
docker compose ps
```

Oodatav tulemus: teenus `db` on olekus `running` või `healthy` ning teenus `client` on olekus `running`.

Kui näed veateadet pordi kohta, näiteks `port is already allocated`, on port `5437` juba kasutusel. Vaata lahendust jaotisest [Levinud vead ja lahendused](#levinud-vead-ja-lahendused).

Kontrolli ka, et `psql` klient saab andmebaasiga ühenduse:

```bash
docker compose exec client psql -c '\conninfo'
```

Oodatav tulemus: `psql` ütleb, et oled ühendatud andmebaasiga `praktikum` hostis `db`.

## 5. Loo skeemid ja toortabel

See samm tehakse hosti terminalis.

Enne skripti käivitamist vaata skeeminimede mõtet. Selles praktikumis kasutame nimesid, mis kirjeldavad andmete turvakihti. Need nimed võivad erineda varasematest praktikumidest, kus fookus oli pigem laadimisel, mudeldamisel või analüütilisel kihil.

Skeeminimed on valitud selle praktikumi eesmärgi järgi:

- `staging` tähendab toorandmete ala, kuhu jõuab algne andmestik;
- `governance` tähendab andmete kirjeldamise ja PII otsuste ala;
- `secured` tähendab turvatud ligipääsukihti, mille kaudu rollid andmeid loevad.

Oluline mõte on see, et toorandmed, andmete kirjeldus ja kasutajatele mõeldud vaated ei asu samas kohas. Nii on hiljem lihtsam selgitada, millele iga roll ligipääsu saab.

Käivita esimene SQL-skript:

```bash
docker compose exec client psql -f scripts/01_create_objects.sql
```

Skript loob need kolm skeemi ja tabeli `staging.osalejad_raw`.

Kontrolli, et tabel on olemas:

```bash
docker compose exec client psql -c '\dt staging.*'
```

Oodatav tulemus: nimekirjas on tabel `staging.osalejad_raw`.

## 6. Laadi sünteetilised osalejaandmed

See samm tehakse hosti terminalis.

Laadi andmed failist `data/osalejad.csv`:

```bash
docker compose exec client psql -f scripts/02_load_data.sql
```

Skript kasutab `\copy` käsku. See loeb `CSV` faili kliendi konteineri teelt `data/osalejad.csv` ja lisab read tabelisse `staging.osalejad_raw`.

Oodatav tulemus:

```text
COPY 12
 laaditud_ridu
---------------
            12
```

Vaata esimesi ridu:

```bash
docker compose exec client psql -c 'SELECT osaleja_id, eesnimi, perenimi, email, linn, kursus FROM staging.osalejad_raw ORDER BY osaleja_id LIMIT 5;'
```

Selles tabelis on ainult väljamõeldud õppeandmed. Käsitle neid siiski nagu päris isikuandmeid, sest töövõte peab olema sama.

## 7. Koosta PII register

See samm tehakse hosti terminalis.

Loo PII register:

```bash
docker compose exec client psql -f scripts/03_create_pii_register.sql
```

PII register on väike tehniline tabel, mis kirjeldab toortabeli veerge. See ei ole kogu andmekataloog ega andmetöötlusregister. Siin kasutad seda ainult selleks, et teha PII otsused nähtavaks enne rollide ja vaadete loomist.

Vaata registrit:

```bash
docker compose exec client psql -c 'SELECT column_name, pii_category, handling_note FROM governance.pii_register ORDER BY sort_order;'
```

Oodatav tulemus: näed iga veeru juures kategooriat `otsene PII`, `kaudne PII` või `ei ole PII`.

Peatu korraks ja mõtle:

- miks `email` on otsene PII;
- miks `linn` on kaudne PII;
- miks `kursus` ei ole üksi PII, aga võib koos nimega muutuda tundlikumaks.

See on andmeturbe oluline osa. Enne õiguste seadmist peab olema selge, mida kaitsta.

## 8. Loo rollid, vaated ja õigused

See samm tehakse hosti terminalis.

Käivita turvaseadistuse skript:

```bash
docker compose exec client psql -f scripts/04_create_roles_and_views.sql
```

Skript käivitatakse vaikerolliga `praktikum`. See roll loob töörollid ja annab neile õigused.

Skript teeb viis asja:

- loob rollid `analyytik`, `aruandlus` ja `auditor`;
- loob maskeeritud vaate `secured.v_osalejad_analyytik`;
- loob koondvaate `secured.v_osalejad_aruandlus`;
- eemaldab tundlikelt objektidelt `PUBLIC` õigused;
- annab igale töörollile ainult vajaliku `SELECT` õiguse.

Kontrolli turvatud vaateid:

```bash
docker compose exec client psql -c '\dv secured.*'
```

Oodatav tulemus: näed vaateid `v_osalejad_analyytik` ja `v_osalejad_aruandlus`.

Vaata õiguste kokkuvõtet:

```bash
docker compose exec client psql -c '\z secured.*'
```

Oodatav tulemus: `analyytik` on seotud analyytiku vaatega, `aruandlus` aruandluse vaatega ja `auditor` mõlema turvatud vaatega.

## 9. Kontrolli rolle ühe skriptiga

See samm tehakse hosti terminalis.

Käivita kontrollskript:

```bash
docker compose exec client psql -f scripts/05_check_results.sql
```

Skript kontrollib:

- millise andmebaasi kasutajana skript töötab;
- mitu rida on toortabelis;
- millised veerud on PII registris;
- millistel rollidel on `SELECT` õigus;
- mida näeb `analyytik`;
- mida näeb `aruandlus`;
- mida näeb `auditor`.

Olulised oodatavad tulemused:

- kontrolli alguses on `current_user` ja `session_user` väärtus `praktikum`;
- `analyytik` ei saa `SELECT` õigust tabelile `staging.osalejad_raw`;
- `analyytik` saab lugeda vaadet `secured.v_osalejad_analyytik`;
- `aruandlus` saab andmevaadetest lugeda ainult koondvaadet;
- `auditor` saab lugeda toortabelit ja mõlemat turvatud vaadet.

Analyytiku väljundis peavad nimi, e-post ja telefon olema maskeeritud. Näiteks e-post kuvatakse kujul `m***@example.test`.

## 10. Proovi keelatud päringut

See samm tehakse `psql` sees.

Ava `psql`:

```bash
docker compose exec client psql
```

Võta analyytiku roll:

```sql
SET ROLE analyytik;
```

Kontrolli, et analyytiku vaade töötab:

```sql
SELECT osaleja_id, email_maskitud, telefon_maskitud
FROM secured.v_osalejad_analyytik
ORDER BY osaleja_id
LIMIT 3;
```

Oodatav tulemus: näed maskeeritud e-posti ja telefoni.

Proovi nüüd sama rolliga lugeda toortabelit:

```sql
SELECT osaleja_id, email, telefon
FROM staging.osalejad_raw
LIMIT 3;
```

Oodatav tulemus on viga:

```text
ERROR:  permission denied for schema staging
```

See viga on siin hea märk. See näitab, et `analyytik` ei pääse toortabelini.

Lülita roll tagasi:

```sql
RESET ROLE;
```

Välju `psql`-ist:

```sql
\q
```

## 11. Tee õiguste kokkuvõte

See samm tehakse hosti terminalis.

Vaata õigusi `psql`-i õiguste vaates:

```bash
docker compose exec client psql -c '\z staging.*'
docker compose exec client psql -c '\z secured.*'
```

Oodatav tulemus:

- `staging.osalejad_raw` juures on näha `auditor` õigus;
- `secured.v_osalejad_analyytik` juures on näha `analyytik` ja `auditor` õigus;
- `secured.v_osalejad_aruandlus` juures on näha `aruandlus` ja `auditor` õigus;
- `analyytik` ja `aruandlus` ei ole toortabeli õiguste juures.

`praktikum` on vaikeroll, millega objektid loodi. Töörollide erinevused tulevad nähtavale eraldi antud õiguste kaudu.

See ongi minimaalõiguste põhimõte praktilisel kujul: tavarollid näevad ainult oma tööks vajalikku vaadet, kontrolliroll saab võrrelda toorandmeid ja jagatavaid vaateid.

## Kontrollpunktid

Praktikumi lõpuks peaksid saama kinnitada järgmised väited:

- `.env` fail on loodud, aga git ignoreerib seda.
- Andmebaasi konteiner `db` ja kliendi konteiner `client` töötavad.
- Tabelis `staging.osalejad_raw` on 12 rida.
- Tabel `governance.pii_register` kirjeldab kõiki toortabeli olulisi veerge.
- Roll `analyytik` näeb maskeeritud vaadet, kuid mitte toortabelit.
- Roll `aruandlus` näeb koondandmeid, kuid mitte reataseme isikuandmeid.
- Roll `auditor` näeb toortabelit ja turvatud vaateid.
- Keelatud päring annab `permission denied` vea.

## Levinud vead ja lahendused

### `.env` fail puudub

**Sümptom:** `docker compose up -d` annab vea, et `.env` faili ei leita või mõni muutuja on tühi.

**Tõenäoline põhjus:** `.env.example` põhjal ei ole veel loodud `.env` faili.

**Lahendus:** loo fail uuesti.

```bash
cp .env.example .env
```

PowerShellis:

```powershell
Copy-Item .env.example .env
```

### Port `5437` on juba kasutusel

**Sümptom:** `docker compose up -d` annab vea `port is already allocated` või `bind: address already in use`.

**Tõenäoline põhjus:** mõni teine PostgreSQL või varasem praktikumi konteiner kasutab sama porti.

**Lahendus:** muuda `.env` failis rida:

```text
DB_PORT_HOST=5438
```

Seejärel käivita konteiner uuesti:

```bash
docker compose up -d
```

### `relation "staging.osalejad_raw" does not exist`

**Sümptom:** andmete laadimine või PII registri kontroll annab vea, et tabelit ei ole olemas.

**Tõenäoline põhjus:** skript `01_create_objects.sql` jäi käivitamata või andmebaas loodi uuesti.

**Lahendus:** käivita esimene skript uuesti:

```bash
docker compose exec client psql -f scripts/01_create_objects.sql
```

### `permission denied for schema staging`

**Sümptom:** `SET ROLE analyytik` järel annab toortabeli päring vea `permission denied`.

**Tõenäoline põhjus:** selles praktikumis on see oodatud tulemus. `analyytik` ei tohi toortabelit lugeda.

**Lahendus:** kasuta analyytiku rolliga maskeeritud vaadet:

```sql
SELECT *
FROM secured.v_osalejad_analyytik
LIMIT 3;
```

### Käsud lähevad valesse kohta

**Sümptom:** terminal ütleb `syntax error`, `command not found` või `invalid command`.

**Tõenäoline põhjus:** SQL-käsk sisestati hosti terminali või terminalikäsk sisestati `psql` sisse.

**Lahendus:** kontrolli prompti.

- Kui näed midagi nagu `praktikum=#`, oled `psql` sees ja sinna käivad SQL-käsud.
- Kui näed kaustateed või `$`, oled hosti terminalis ja sinna käivad `docker compose ...` käsud.

`psql`-ist väljumiseks kasuta:

```sql
\q
```

## Kokkuvõte

Selles praktikumis tegid läbi väikese andmeturbe töövoo.

Sa lõid toortabeli, laadisid sinna sünteetilised andmed, kirjeldasid PII veerud registris ja seadsid üles kolm töörolli. Oluline mõte on see, et roll ei pea nägema toortabelit ainult sellepärast, et tal on vaja andmetega tööd teha. Sageli piisab maskeeritud vaatest või koondvaatest. Kontrolliroll on erandlik: tema ligipääs peab aitama õigusi ja vaateid kontrollida.

Tööelus on sama põhimõte suurem ja rangem, aga tuum on sama:

- tea, millised andmed on tundlikud;
- hoia saladused koodist väljas;
- anna rollile ainult vajalik ligipääs;
- kontrolli õigusi päriselt, mitte ainult eelda, et need töötavad.

## Valikuline lisaharjutus

Loo uus roll `juhendaja`.

`juhendaja` peab nägema osaleja linna, maakonda, kursust ja staatust, kuid mitte nime, e-posti ega telefoni.

Soovitatud töö:

1. loo roll `juhendaja`;
2. loo vaade `secured.v_osalejad_juhendaja`;
3. anna rollile `USAGE` õigus skeemile `secured`;
4. anna rollile `SELECT` õigus ainult sellele vaatele;
5. testi tulemust käsuga `SET ROLE juhendaja`.

Vihje vaate alguseks:

```sql
CREATE OR REPLACE VIEW secured.v_osalejad_juhendaja AS
SELECT
    osaleja_id,
    linn,
    maakond,
    kursus,
    staatus
FROM staging.osalejad_raw;
```

Kontrollküsimus: kas `osaleja_id` peaks selles vaates olema? Põhjenda oma otsust PII registri põhjal.

### Järgmised sammud

Kui põhirada on tehtud ja tahad teemat edasi uurida, vali üks järgmistest suundadest.

**1. Laienda sama SQL-lahendust.**

Lisa veel üks vaade, kus `registreerumise_kuupaev` on ümardatud kuu tasemele. See aitab harjutada mõtet, et ka kuupäev võib koos teiste väljadega inimest eristada.

Näiteks:

```sql
date_trunc('month', registreerumise_kuupaev)::date AS registreerumise_kuu
```

Kontrolli ka, kas mõni koondrühm on liiga väike. Näiteks saad otsida linn + kursus + staatus kombinatsioone, kus on vähem kui 3 rida:

```sql
SELECT linn, kursus, staatus, COUNT(*) AS ridade_arv
FROM staging.osalejad_raw
GROUP BY linn, kursus, staatus
HAVING COUNT(*) < 3;
```

See ei tee andmeid automaatselt anonüümseks, kuid aitab näha k-anonüümsuse põhiideed.

**2. Vaata, kuidas sama mõte viiakse dbt-sse.**

Praktikas on `dbt` sageli vaikimisi tööriist analüütiliste SQL-mudelite, testide ja dokumentatsiooni haldamiseks. Selles baastaseme praktikumis on rollid ja vaated eraldi SQL-skriptides. Suuremas projektis tekib kiiresti küsimus: kuidas hoida PII veergude kirjeldus, maskeerimisreeglid ja vaated koodis nii, et need oleksid korduvkäivitatavad ja testitavad.

Seda teeb edasijõudnute praktikum dbt abil:

- PII info kirjeldatakse `schema.yml` failis;
- maskeerimist teevad dbt makrod;
- turvatud vaated ehitatakse dbt mudelitena;
- teste kasutatakse selleks, et keelatud veerud ei ilmuks valesse vaatesse.

Vaata kõrvale [edasijõudnute 7. praktikumi juhendit](../edasijoudnud/README.md). Sa ei pea kõike kaasa tegema. Alusta jaotistest “Arhitektuur”, “Metaandmed dbt-s” ja “RBAC: rollid ja grants”.

**3. Vaata, kuidas PII info elaks andmekataloogis.**

Siin hoidsid PII infot tabelis `governance.pii_register`, et otsused oleksid SQL-is nähtavad. Päris projektis hoitakse sellist infot sageli andmekataloogis.

Hea edasiuurimise tööriist on [`OpenMetadata`](https://docs.open-metadata.org/v1.11.x/how-to-guides/data-governance/classification). Vaata sealt eriti klassifikatsioonide, siltide ja ärisõnastiku mõtet. Küsi endalt: kuidas leida kõik tabelid või veerud, mis on märgitud PII-na?

**4. Mõtle, mis jääb andmebaasi ja mis kuulub andmeplatvormi.**

Selles praktikumis hoiab PostgreSQL rolle ja õigusi. Pilveandmeladudes on sama põhimõte tavaliselt seotud platvormi enda õiguste kihiga, näiteks Snowflake'i rollid, BigQuery IAM või Databricksi Unity Catalog. Tööriist muutub, kuid küsimus jääb samaks: milline roll näeb toorandmeid, milline maskeeritud andmeid ja milline ainult koondeid?

## Koristamine

Kui tahad eemaldada ainult praktikumi andmebaasi objektid, jäta konteinerid tööle ja käivita:

```bash
docker compose exec client psql -f scripts/99_reset.sql
```

Kui tahad peatada konteineri, aga andmemahu alles jätta:

```bash
docker compose down
```

Kui tahad täiesti puhast algust ja kustutada ka andmemahu:

```bash
docker compose down -v
```
