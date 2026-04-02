# Praktikum 7: Andmeturve ja privaatsus (Edasijõudnud)

## Eesmärk

Kujundada rollid ja vaated nii, et tundlikud andmed on maskeeritud. Praktikumi lõpuks oskad analüüsida auditit toetavaid logisid ja rakendada andmekaitse põhimõtteid praktikas.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Oskab kujundada rolle ja vaateid nii, et osa andmeid on maskeeritud
- Suudab vaadelda ja analüüsida auditit toetavaid logisid
- Mõistab GDPR ja andmekaitse põhiprintsiipe andmeinseneeria kontekstis
- Oskab rakendada veerupõhist ligipääsukontrolli

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| Andmete maskeerimine | Tundlike andmete peitmine vaadetes ja päringutes |
| Audit log | Ligipääsude ja muudatuste jälgimine logidega |
| GDPR | Euroopa andmekaitsemäärus ja selle nõuded |
| Veerupõhine ligipääs | Erinevad rollid näevad erinevaid veerge |
| Row-Level Security | Reapõhine ligipääsukontroll PostgreSQL-is |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Kogemus PostgreSQL-iga (GRANT, REVOKE, VIEW-d)
- Arusaam PII-st ja rollipõhisest ligipääsust (baastase teadmised)

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Andmete maskeerimine** | Tundlike andmete asendamine (nt `****1234`) nii, et andmestruktuur säilib |
| **Audit log** | Logi, mis salvestab kes, millal ja mida andmetega tegi |
| **GDPR** | General Data Protection Regulation — EL-i andmekaitsemäärus |
| **Row-Level Security (RLS)** | PostgreSQL mehhanism, mis piirab ridade nähtavust rolli põhjal |
| **Column-Level Security** | Ligipääsukontroll üksikute veergude tasemel |
