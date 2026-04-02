# Praktikum 4: Andmetorude orkestreerimine (Edasijõudnud)

## Eesmärk

Luua Airflow DAG ja jooksutada seda orkestreerijas. Praktikumi lõpuks oskad seoda laadimise ja testid ühte juhitavasse töövoogu.

## Õpiväljundid

Praktikumi lõpuks osaleja:

- Oskab luua Airflow DAG-i ja jooksutada seda orkestreerijas
- Suudab defineerida ülesannete sõltuvusi ja järjekorda
- Seob andmete laadimise ja kvaliteeditestid ühte juhitavasse töövoogu
- Mõistab orkestreerimise põhimõtteid (retry, alerting, backfill)

## Teemad

| Teema | Kirjeldus |
|-------|-----------|
| Airflow | Töövoogude orkestreerimise platvorm |
| DAG | Suunatud atsükliline graaf ülesannete kirjeldamiseks |
| Operaatorid | Airflow operaatorid (BashOperator, PythonOperator jt) |
| Sõltuvused | Ülesannete vahelised sõltuvused ja nende defineerimine |
| Monitoring | Töövoogude jälgimine, alertid ja logid |

## Eeldused

- Docker ja Docker Compose on paigaldatud
- Kogemus PostgreSQL, SQL ja Python-iga
- Arusaam CRON ajastusest (baastase teadmised)
- Töötav ETL protsess eelmistest praktikumidest

## Uued mõisted

| Mõiste | Selgitus |
|--------|----------|
| **Airflow** | Apache Airflow — avatud lähtekoodiga töövoogude orkestreerimise platvorm |
| **DAG** | Directed Acyclic Graph — suunatud atsükliline graaf, mis kirjeldab ülesannete järjekorda |
| **Operaator** | Airflow ülesande tüüp (nt BashOperator käivitab shelli käsu) |
| **Backfill** | Möödunud perioodi andmete tagantjärele töötlemine |
| **XCom** | Airflow mehhanism ülesannete vaheliseks andmevahetuseks |
