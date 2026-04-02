# Praktikum 8: Reaalajas andmetöötlus (Edasijõudnud)

## Eesmärk

Tutvuda Apache Kafka põhikontseptsioonidega ja teha transformatsioone voogandmetel. Praktikumi lõpuks oskad selgitada Kafka arhitektuuri ja kirjutada väljundi sihtkohta.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Oskab selgitada Apache Kafka põhikontseptsioone (topic, partition, consumer group)
- Suudab teha transformatsioone voogandmetel
- Oskab kirjutada töödeldud andmed väljundi sihtkohta (andmebaas, fail)
- Mõistab at-least-once ja exactly-once semantikat

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| Apache Kafka | Hajutatud sündmuste voogedastusplatvorm |
| Topic ja Partition | Kafka andmete organiseerimise struktuur |
| Producer ja Consumer | Andmete saatmine ja vastuvõtmine Kafkas |
| Transformatsioonid | Voogandmete töötlemine reaalajas |
| Delivery semantika | At-least-once, at-most-once, exactly-once garantiid |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Kogemus Python-iga
- Arusaam sündmustest ja pub/sub mudelist (baastase teadmised)

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Apache Kafka** | Hajutatud sündmuste voogedastusplatvorm suure läbilaskevõimega |
| **Topic** | Kafka loogiline kanal, kuhu sõnumid avaldatakse |
| **Partition** | Topic-i alamjaotus, mis võimaldab paralleeltöötlust |
| **Consumer Group** | Tarbijate rühm, kes jagavad topic-i partitsioonid omavahel |
| **Offset** | Sõnumi järjekorranumber partitsioonisiseselt |
| **Exactly-once** | Garantii, et iga sõnumit töödeldakse täpselt üks kord |
