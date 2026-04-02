# Praktikum 5: Suurandmed ja pilvelahendused (Edasijõudnud)

## Eesmärk

Teha Spark DataFrame põhiseid transformatsioone ja mõista kaasaegseid andmejärvi. Praktikumi lõpuks oskad põhjendada partitsioneerimise valikut ja tead, kus data lakehouse lahendust praktikas kasutatakse.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Oskab teha Spark DataFrame põhiseid transformatsioone
- Suudab põhjendada partitsioneerimise valikut (mille järgi ja miks)
- Mõistab kaasaegsete andmejärvede (data lakehouse) arhitektuuri
- Teab, kus ja miks neid lahendusi praktikas kasutatakse

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| Spark | Hajusandmetöötluse raamistik ja DataFrame API |
| Partitsioneerimine | Andmete jagamine loogilisteks osadeks jõudluse parandamiseks |
| Data Lakehouse | Data Lake + Data Warehouse omaduste kombinatsioon |
| Delta Lake | Avatud tabeliformaat ACID transaktsioonidega |

## Eeldused

- Kogemus Python-iga
- Põhiteadmised SQL-ist
- Arusaam Parquet formaadist ja hajussüsteemidest (baastase teadmised)

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Spark** | Apache Spark — hajusandmetöötluse raamistik suurte andmemahtude jaoks |
| **DataFrame** | Spark-i tabelilaadne andmestruktuur, mida saab transformeerida |
| **Partitsioneerimine** | Andmete jagamine osadeks (nt kuupäeva järgi) päringute kiirendamiseks |
| **Delta Lake** | Avatud tabeliformaat, mis lisab andmejärvele ACID garantiid |
| **ACID** | Atomicity, Consistency, Isolation, Durability — andmebaaside usaldusväärsuse tagatis |
