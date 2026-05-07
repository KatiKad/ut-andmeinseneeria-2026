"""
Andmete sissetoomise skript (ingest.py)

Laeb andmeid kahest API-st PostgreSQL staging skeemasse:
  - randomuser.me   -> staging.users   (kasutajaprofiilid)
  - jsonplaceholder  -> staging.posts   (postitused)

Kasutamine:
  python ingest.py users                  # Laadi 10 kasutajat
  python ingest.py posts                  # Laadi kõik postitused (1-100)
  python ingest.py posts --batch 1        # Laadi postitused 1-50
  python ingest.py posts --batch 2        # Laadi postitused 51-100
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import psycopg2
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --- Andmebaasiuhendus ---

def get_connection():
    """Loo andmebaasiühendus keskkonnamuutujate põhjal."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )

# --- Skeema ja tabelite loomine ---

SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS staging;"

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS staging.users (
    id          SERIAL PRIMARY KEY,
    uuid        TEXT UNIQUE NOT NULL,
    first_name  TEXT,
    last_name   TEXT,
    email       TEXT,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    street      TEXT,
    postcode    TEXT,
    registered_date TIMESTAMP,
    loaded_at   TIMESTAMP DEFAULT NOW()
);
"""

POSTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS staging.posts (
    id          INT PRIMARY KEY,
    user_id     INT NOT NULL,
    title       TEXT,
    body        TEXT,
    loaded_at   TIMESTAMP DEFAULT NOW()
);
"""

ETL_LOG_SQL = """
CREATE TABLE IF NOT EXISTS staging.etl_log (
    id          SERIAL PRIMARY KEY,
    source      TEXT NOT NULL,
    started_at  TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    rows_loaded INT DEFAULT 0,
    status      TEXT DEFAULT 'running',
    error_msg   TEXT
);
"""

def ensure_tables(conn):
    """Loo staging skeema ja tabelid, kui neid pole."""
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
        cur.execute(USERS_TABLE_SQL)
        cur.execute(POSTS_TABLE_SQL)
        cur.execute(ETL_LOG_SQL)
    conn.commit()

# --- ETL logimine ---

def log_start(conn, source):
    """Salvesta ETL algusaeg ja tagasta log ID."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO staging.etl_log (source, started_at) VALUES (%s, %s) RETURNING id;",
            (source, datetime.now()),
        )
        log_id = cur.fetchone()[0]
    conn.commit()
    return log_id


def log_finish(conn, log_id, rows_loaded, status="success", error_msg=None):
    """Uuenda ETL logi lopptulemusega."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE staging.etl_log
               SET finished_at = %s, rows_loaded = %s, status = %s, error_msg = %s
               WHERE id = %s;""",
            (datetime.now(), rows_loaded, status, error_msg, log_id),
        )
    conn.commit()

# --- Kasutajate laadimine ---

USERS_API_URL = "https://randomuser.me/api/?results=10&seed=praktikum&inc=name,location,email,registered,login"

UPSERT_USER_SQL = """
INSERT INTO staging.users (uuid, first_name, last_name, email, city, state, country, street, postcode, registered_date, loaded_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (uuid) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    country = EXCLUDED.country,
    street = EXCLUDED.street,
    postcode = EXCLUDED.postcode,
    registered_date = EXCLUDED.registered_date,
    loaded_at = NOW();
"""


def load_users(conn):
    """Laadi kasutajad randomuser.me API-st staging.users tabelisse."""
    log_id = log_start(conn, "randomuser.me/users")
    rows = 0

    try:
        logger.info("Pärin kasutajaid: %s", USERS_API_URL)
        resp = requests.get(USERS_API_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        with conn.cursor() as cur:
            for user in data["results"]:
                loc = user["location"]
                street = f"{loc['street']['number']} {loc['street']['name']}"
                cur.execute(UPSERT_USER_SQL, (
                    user["login"]["uuid"],
                    user["name"]["first"],
                    user["name"]["last"],
                    user["email"],
                    loc["city"],
                    loc["state"],
                    loc["country"],
                    street,
                    str(loc["postcode"]),
                    user["registered"]["date"],
                ))
                rows += 1
        conn.commit()
        logger.info("Laaditud %d kasutajat.", rows)
        log_finish(conn, log_id, rows)

    except Exception as e:
        conn.rollback()
        logger.error("Kasutajate laadimine ebaõnnestus: %s", e)
        log_finish(conn, log_id, rows, status="error", error_msg=str(e))
        raise

# --- Postituste laadimine ---

POSTS_API_URL = "https://jsonplaceholder.typicode.com/posts"

UPSERT_POST_SQL = """
INSERT INTO staging.posts (id, user_id, title, body, loaded_at)
VALUES (%s, %s, %s, %s, NOW())
ON CONFLICT (id) DO NOTHING;
"""


def load_posts(conn, batch=None):
    """Laadi postitused jsonplaceholder API-st staging.posts tabelisse.

    batch=1  -> postitused 1-50
    batch=2  -> postitused 51-100
    batch=None -> kõik postitused 1-100
    """
    label = f"jsonplaceholder/posts/batch-{batch or 'all'}"
    log_id = log_start(conn, label)
    rows = 0

    try:
        logger.info("Pärin postitusi: %s", POSTS_API_URL)
        resp = requests.get(POSTS_API_URL, timeout=30)
        resp.raise_for_status()
        posts = resp.json()

        if batch == 1:
            posts = [p for p in posts if p["id"] <= 50]
        elif batch == 2:
            posts = [p for p in posts if p["id"] > 50]

        with conn.cursor() as cur:
            for post in posts:
                cur.execute(UPSERT_POST_SQL, (
                    post["id"],
                    post["userId"],
                    post["title"],
                    post["body"],
                ))
                rows += 1
        conn.commit()
        logger.info("Laaditud %d postitust (batch=%s).", rows, batch or "all")
        log_finish(conn, log_id, rows)

    except Exception as e:
        conn.rollback()
        logger.error("Postituste laadimine ebaõnnestus: %s", e)
        log_finish(conn, log_id, rows, status="error", error_msg=str(e))
        raise

# --- Peamine ---

def main():
    parser = argparse.ArgumentParser(description="Andmete sissetoomine API-st PostgreSQL-i.")
    parser.add_argument("source", choices=["users", "posts"], help="Andmeallikas: users voi posts")
    parser.add_argument("--batch", type=int, choices=[1, 2], default=None, help="Postituste partii (1=1-50, 2=51-100)")
    args = parser.parse_args()

    conn = get_connection()
    try:
        ensure_tables(conn)

        if args.source == "users":
            load_users(conn)
        elif args.source == "posts":
            load_posts(conn, batch=args.batch)
    finally:
        conn.close()

    logger.info("Valmis.")


if __name__ == "__main__":
    main()
