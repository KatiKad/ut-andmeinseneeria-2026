# Praktikum 7: Andmeturve ja privaatsus (Baastase)

## Eesmärk

Õppida tundlikke andmeid turvaliselt käsitlema. Praktikumi lõpuks mõistad PII mõistet, oskad rakendada rollipõhist ligipääsu ja tead, kuidas saladusi turvaliselt hoida.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Mõistab PII (isikuandmete) mõistet ja oskab tundlikke andmeid tuvastada
- Oskab rakendada lihtsat rollipõhist ligipääsu (RBAC) andmebaasis
- Teab, mida ei tohi git reposse laadida (paroolid, võtmed, `.env` failid)
- Oskab saladusi ja ligipääse turvaliselt hoida

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| PII | Isiku tuvastamist võimaldavad andmed ja nende kaitse |
| RBAC | Rollipõhine ligipääsukontroll andmebaasis |
| Saladuste haldus | `.env` failid, `.gitignore`, keskkonnamuutujad |
| Minimaalõigused | Kasutajale antakse ainult vajalikud õigused |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Eelmiste praktikumide kogemus PostgreSQL-iga
- Põhiteadmised SQL-ist (GRANT, REVOKE)

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **PII** | Personally Identifiable Information — isikut tuvastada võimaldavad andmed |
| **RBAC** | Role-Based Access Control — rollipõhine ligipääsukontroll |
| **Minimaalõigused** | Printsiip, kus kasutaja saab ainult tööks vajalikud õigused |
| **`.env`** | Keskkonnamuutujate fail, mis hoiab tundlikku konfiguratsiooni väljaspool koodi |
| **`.gitignore`** | Fail, mis määrab, milliseid faile git ei jälgi (nt `.env`, paroolid) |
