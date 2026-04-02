# Praktikum 4: Andmetorude orkestreerimine (Baastase)

## Eesmärk

Õppida andmetöötluse skripte automaatselt ajastama ja käivitama. Praktikumi lõpuks oskad automatiseerida skripti käivitust CRON ajastusega ja koguda töö logisid.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Oskab automatiseerida skripti käivitust CRON ajastusega
- Suudab koguda ja analüüsida töö logisid
- Mõistab sõltuvuste ja uuesti proovimise (retry) põhimõtteid
- Tunneb ajastatud töövoogude tüüpilisi probleeme ja lahendusi

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| CRON | Ajastusreeglite süntaks ja seadistamine |
| Logimine | Skripti väljundi salvestamine ja vigade jälgimine |
| Sõltuvused | Ülesannete järjekorra ja sõltuvuste haldamine |
| Retry | Ebaõnnestunud ülesannete automaatne kordamine |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Eelmiste praktikumide kogemus PostgreSQL ja Python-iga
- Töötav ETL skript eelmisest praktikumist

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **CRON** | Unixi ajastussüsteem, mis käivitab ülesandeid kindlal ajal |
| **CRON-avaldis** | Viieosaline ajamuster, nt `0 8 * * *` = iga päev kell 8 |
| **Orkestreerimine** | Mitme andmetöötluse sammu koordineeritud juhtimine |
| **Retry** | Ebaõnnestunud ülesande automaatne uuesti proovimine |
