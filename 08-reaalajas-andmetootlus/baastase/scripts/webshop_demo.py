"""Käsurea abiskript baastaseme veebipoe sündmuste praktikumile.

See fail on näite publisher'i ehk sündmuste avaldaja pool.

Õppija käivitab näiteks sellise käsu:

    python scripts/webshop_demo.py publish --count 10

Käsk loob veebipoe tellimuse sündmused, salvestab need PostgreSQL-i ja saadab
iga sündmuse kohta ühe Celery tööülesande Redisesse. Hiljem töötleb neid
`celery_app.py` failis olev Celery worker.

Kui Python on sulle uus, loe faili selles järjekorras:

1. `parse_args()`, et näha käsurea käske.
2. `publish()`, et näha tavalist sündmuse avaldamise voogu.
3. `enqueue_event()`, et näha, kus Celery mängu tuleb.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import psycopg2
import redis
from psycopg2.extras import Json

from scripts.celery_app import process_order_event


SOURCE_DATA_DIR = Path("source_data")
DEFAULT_QUEUE_NAME = "celery"


def get_connection():
    """Loo PostgreSQL-i ühendus samade `.env` väärtustega nagu worker."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )


def get_redis_client():
    """Loo Redise klient väikeste järjekorrakontrollide jaoks.

    Celery räägib Redisega ise, kui käivitame `process_order_event.delay(...)`.
    Seda abifunktsiooni kasutavad ainult õppijale nähtavad käsud
    `queue-status` ja `clear-queue`.
    """
    broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    return redis.Redis.from_url(broker_url)


def utc_now() -> datetime:
    """Tagasta praegune UTC ajatempel koos ajavööndiga.

    UTC (`Coordinated Universal Time`, koordineeritud maailmaaeg) aitab hoida
    konteinerites ajatemplid ühtsel kujul.
    """
    return datetime.now(timezone.utc)


def read_csv_dicts(path: Path) -> list[dict]:
    """Loe väike CSV-fail sõnastike loendiks."""
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_products() -> list[dict]:
    """Loe väikese veebipoe näite tooteandmed."""
    return read_csv_dicts(SOURCE_DATA_DIR / "products.csv")


def load_stores() -> list[dict]:
    """Loe väikese veebipoe näite poeandmed."""
    return read_csv_dicts(SOURCE_DATA_DIR / "stores.csv")


def build_payload(*, event_time: datetime, index: int, bad_event: bool = False) -> tuple[str, str, dict]:
    """Ehita ühe veebipoe tellimuse sündmuse sisu.

    Andmed on teadlikult lihtsad. Valime CSV-failidest toote ja poe, loome
    koguse ja hinna ning tagastame sündmuse tüübi, sündmuse võtme ja JSON
    kujul sisu.

    `bad_event=True` teeb koguseks nulli. Worker peaks selle tagasi lükkama ja
    kirjutama sündmuse tabelisse `staging.bad_events`.
    """
    products = load_products()
    stores = load_stores()

    product = products[index % len(products)]
    store = stores[index % len(stores)]
    quantity = (index % 4) + 1
    unit_price = Decimal(product["base_price_eur"]) + Decimal(str((index % 3) * 0.5))
    order_id = f"ORD-{event_time.strftime('%Y%m%d%H%M%S')}-{index + 1:03d}-{uuid.uuid4().hex[:6]}"

    payload = {
        "order_id": order_id,
        "store_id": store["store_id"],
        "product_id": product["product_id"],
        "quantity": quantity,
        "unit_price_eur": str(unit_price.quantize(Decimal("0.01"))),
        "source": "veebipood",
    }

    if bad_event:
        payload["quantity"] = 0

    event_key = store["store_id"]
    event_type = "order_created"
    return event_type, event_key, payload


def insert_event(conn, *, event_id: str, event_type: str, event_key: str, event_time: datetime, payload: dict) -> None:
    """Lisa üks sündmus nähtavasse PostgreSQL-i sündmuste logisse."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO stream.event_log (
                event_id,
                event_type,
                event_key,
                event_time,
                payload,
                status
            )
            VALUES (%s, %s, %s, %s, %s, 'published')
            """,
            (event_id, event_type, event_key, event_time, Json(payload)),
        )
    conn.commit()


def enqueue_event(conn, *, event_id: str, dispatch_kind: str = "initial") -> str:
    """Saada üks Celery tööülesanne Redisesse ja logi saatmine PostgreSQL-is.

    Celery sõnum sisaldab ainult `event_id` väärtust. Sündmuse sisu ja oleku
    õppijale nähtav allikas jääb PostgreSQL.
    """
    async_result = process_order_event.delay(event_id)
    queued_at = utc_now()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE stream.event_log
            SET
                queued_at = COALESCE(queued_at, %s),
                status = CASE
                    WHEN status = 'published' THEN 'queued'
                    ELSE status
                END,
                celery_task_id = COALESCE(celery_task_id, %s)
            WHERE event_id = %s
            """,
            (queued_at, async_result.id, event_id),
        )
        cur.execute(
            """
            INSERT INTO stream.task_dispatch_log (
                event_id,
                celery_task_id,
                dispatch_kind,
                queued_at
            )
            VALUES (%s, %s, %s, %s)
            """,
            (event_id, async_result.id, dispatch_kind, queued_at),
        )
    conn.commit()
    return async_result.id


def publish(args) -> None:
    """Loo veebipoe tellimuse sündmused ja pane need worker'i jaoks järjekorda."""
    count = args.count
    if args.scenario == "late-event" and args.count == 10:
        # Tavalise avaldamise puhul on vaikimisi arv mugav. Hilinenud sündmuse
        # harjutuses on üht sündmust SQL-i väljundis lihtsam uurida.
        count = 1

    conn = get_connection()
    try:
        base_time = utc_now()
        published = []
        for index in range(count):
            event_id = str(uuid.uuid4())

            if args.scenario == "late-event":
                # Simuleerime sündmust, mis juhtus kaheksa minutit tagasi, kuid
                # avaldatakse alles nüüd. Nii muutuvad sündmuse aeg ja töötluse
                # aeg silmaga nähtavalt erinevaks.
                event_time = utc_now() - timedelta(minutes=8)
            else:
                # Simuleerime väikest ajavahet tellimuste tekkimise vahel.
                event_time = base_time - timedelta(seconds=(count - index) * 10)

            bad_event = args.include_bad_event and index == count - 1
            event_type, event_key, payload = build_payload(
                event_time=event_time,
                index=index,
                bad_event=bad_event,
            )
            insert_event(
                conn,
                event_id=event_id,
                event_type=event_type,
                event_key=event_key,
                event_time=event_time,
                payload=payload,
            )
            task_id = enqueue_event(conn, event_id=event_id)
            published.append((event_id, task_id, payload["order_id"]))
            print(
                "Avaldatud "
                f"event_id={event_id} task_id={task_id} order_id={payload['order_id']}",
                flush=True,
            )
            if args.delay_seconds > 0:
                time.sleep(args.delay_seconds)

        print(f"Kokku avaldati {len(published)} sündmust.")
    finally:
        conn.close()


def queue_status(_args) -> None:
    """Prindi Redise järjekorra pikkus ja sündmuste olekud PostgreSQL-is."""
    client = get_redis_client()
    queued_tasks = client.llen(DEFAULT_QUEUE_NAME)
    print(f"Redise järjekorras `{DEFAULT_QUEUE_NAME}` on {queued_tasks} tööülesannet.")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, COUNT(*)
                FROM stream.event_log
                GROUP BY status
                ORDER BY status
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("stream.event_log on tühi.")
        return

    print("Sündmuste olek PostgreSQL-is:")
    for status, count in rows:
        print(f"- {status}: {count}")


def enqueue_duplicate(_args) -> None:
    """Pane viimane sündmus teist korda Celery järjekorda.

    Seda käsku kasutatakse idempotentsuse näitamiseks. Worker võib sama sündmust
    uuesti näha, kuid analüütika tabelid ei tohiks teist korda muutuda.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id
                FROM stream.event_log
                ORDER BY published_at DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()

        if row is None:
            print("Ei leidnud ühtegi sündmust, mida uuesti järjekorda panna.")
            return

        event_id = row[0]
        task_id = enqueue_event(conn, event_id=event_id, dispatch_kind="duplicate")
        print(f"Sama sündmus pandi uuesti järjekorda: event_id={event_id} task_id={task_id}")
    finally:
        conn.close()


def clear_queue(_args) -> None:
    """Tühjenda Celery Redise järjekord ja salvestatud tööülesannete tulemused.

    See ei tühjenda PostgreSQL-i tabeleid. Kui on vaja puhast praktikumi seisu,
    kasutab README seda käsku koos failiga `scripts/99_reset.sql`.
    """
    client = get_redis_client()
    deleted = client.delete(DEFAULT_QUEUE_NAME)

    result_keys = list(client.scan_iter(match="celery-task-meta-*"))
    if result_keys:
        client.delete(*result_keys)

    print(
        "Redise järjekord puhastatud. "
        f"Kustutatud järjekorra võtmeid: {deleted}; kustutatud tulemuste kirjeid: {len(result_keys)}."
    )


def print_last_events(_args) -> None:
    """Prindi viimased sündmuste logi read lihtsate JSON loenditena."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id, event_type, event_time, published_at, queued_at, processed_at, status
                FROM stream.event_log
                ORDER BY published_at DESC
                LIMIT 10
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("Sündmuseid ei ole veel.")
        return

    for row in rows:
        print(json.dumps([str(value) for value in row], ensure_ascii=False))


def parse_args():
    """Kirjelda README-s kasutatav väike käsurealiides."""
    parser = argparse.ArgumentParser(description="Praktikum 8 veebipoe sündmuste demo.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    publish_parser = subparsers.add_parser("publish", help="Avalda veebipoe müügisündmuseid.")
    publish_parser.add_argument("--count", type=int, default=10)
    publish_parser.add_argument("--delay-seconds", type=float, default=0)
    publish_parser.add_argument("--include-bad-event", action="store_true")
    publish_parser.add_argument("--scenario", choices=["normal", "late-event"], default="normal")
    publish_parser.set_defaults(func=publish)

    queue_parser = subparsers.add_parser("queue-status", help="Näita Redise järjekorra ja andmebaasi olekut.")
    queue_parser.set_defaults(func=queue_status)

    duplicate_parser = subparsers.add_parser(
        "enqueue-duplicate",
        help="Pane viimane sündmus uuesti Celery järjekorda.",
    )
    duplicate_parser.add_argument("--last-event", action="store_true", help="Loetavuse jaoks. Vaikimisi kasutatakse viimast sündmust.")
    duplicate_parser.set_defaults(func=enqueue_duplicate)

    clear_parser = subparsers.add_parser("clear-queue", help="Puhasta Celery järjekord Redises.")
    clear_parser.set_defaults(func=clear_queue)

    events_parser = subparsers.add_parser("last-events", help="Näita viimaseid sündmuseid.")
    events_parser.set_defaults(func=print_last_events)

    return parser.parse_args()


def main() -> None:
    """Käivita kasutaja valitud käsk."""
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
