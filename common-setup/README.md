# Ühised seadistused ja Docker konfiguratsioonid

Siin kaustas hoitakse jagatud konfiguratsioone, mida kasutatakse mitme praktikumi üleselt.

## Eeldused

Kõikide praktikumide jaoks on vajalik:

- **Docker Desktop** — konteinerite käivitamiseks ([paigaldusjuhend](https://docs.docker.com/get-docker/))
- **Git** — lähtekoodi haldamiseks ([paigaldusjuhend](https://git-scm.com/downloads))
- **Tekstiredaktor** — koodi ja konfiguratsioonifailide muutmiseks (nt VS Code)
- **Terminal** — käsurea kasutamiseks (Windows: Git Bash / WSL, macOS: Terminal, Linux: Terminal)

## Docker põhikäsud

| Käsk | Kirjeldus |
|------|-----------|
| `docker compose up -d` | Käivita teenused taustal |
| `docker compose down` | Peata ja eemalda teenused |
| `docker compose ps` | Vaata jooksvate teenuste olekut |
| `docker compose logs -f` | Vaata teenuste logisid reaalajas |
| `docker compose down -v` | Peata teenused ja kustuta andmemahud (volumes) |

## `.env` fail

Iga praktikumi kaustas on `.env.example` fail, mille põhjal tuleb luua `.env` fail. See sisaldab keskkonnamuutujaid (nt andmebaasi kasutajanimi ja parool).

```bash
cp .env.example .env
```

> **NB!** `.env` faile ei tohi git reposse laadida. Need on `.gitignore` abil välistatud.
