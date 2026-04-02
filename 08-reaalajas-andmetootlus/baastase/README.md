# Praktikum 8: Reaalajas andmetöötlus (Baastase)

## Eesmärk

Tutvuda sündmuspõhise arhitektuuriga ja reaalajaandmetöötluse põhimõtetega. Praktikumi lõpuks mõistad, mis on sündmus, oskad teha lihtsa publish/subscribe simulatsiooni ja salvestada tulemuse tabelisse.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Mõistab, mis on sündmus ja miks reaalajaandmetöötlust vaja on
- Suudab teha lihtsa simulatsiooni kasutades publish/subscribe mudelit
- Oskab salvestada voogandmete tulemuse andmebaasi tabelisse
- Tunneb erinevust pakktöötluse (batch) ja voogandmetöötluse (streaming) vahel

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| Sündmused | Mis on sündmus ja sündmuspõhine arhitektuur |
| Pub/Sub | Publish/subscribe mudel ja selle kasutamine |
| Batch vs Streaming | Pakktöötluse ja voogandmetöötluse erinevused |
| Andmete salvestamine | Voogandmete tulemuste salvestamine tabelisse |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Eelmiste praktikumide kogemus PostgreSQL ja Python-iga

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Sündmus (Event)** | Miski, mis juhtub kindlal ajahetkel (nt ost, klõps, anduri lugemine) |
| **Publish/Subscribe** | Muster, kus saatja (publisher) saadab sõnumi ja vastuvõtjad (subscribers) kuulavad |
| **Streaming** | Andmete pidev töötlemine nende saabumise järjekorras |
| **Batch** | Andmete töötlemine kogumitena kindlatel ajahetkedel |
| **Sõnumijärjekord** | Vahendaja, mis hoiab sõnumeid saatja ja vastuvõtja vahel |
