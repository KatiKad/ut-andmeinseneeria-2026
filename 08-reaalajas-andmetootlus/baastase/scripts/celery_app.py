"""Celery worker baastaseme reaalajas andmetöötluse praktikumi jaoks.

See fail on veebipoe näite worker'i pool.

Kui Python on sulle uus, loe faili selles järjekorras:

1. Celery seadistus faili alguses.
2. `process_order_event`, mida worker iga sündmuse jaoks käivitab.
3. Väiksemad abifunktsioonid, mida töötlus kasutab.

Oluline õpitav mõte on järgmine:

- Redis hoiab järjekorras tööülesannet.
- Celery kutsub välja `process_order_event(event_id)`.
- PostgreSQL hoiab nähtavat sündmuste logi ja analüütika tabeleid.

Kood on teadlikult otsekohene. Päris teenuses jagaksime osa sellest väiksemateks
mooduliteks, aga praktikumis on kasulik näha üht terviklikku sündmuse teekonda
ühes failis.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import psycopg2
from celery import Celery
from psycopg2.extras import Json


BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

# Celery vajab maaklerit. Selles praktikumis on maakler Redis.
# Tulemuste taustahoidla on samuti Redis, kuid praktikumi oluline väljund on
# PostgreSQL-is, et seda saaks SQL-iga uurida.
celery_app = Celery("praktikum8", broker=BROKER_URL, backend=RESULT_BACKEND)
app = celery_app
celery_app.conf.update(
    # Kinnitame tööülesande alles pärast töö lõppu. Nii on tõrkeid lihtsam
    # mõista, sest katkenud tööülesanne võib uuesti järjekorda jõuda.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Ühe worker-protsessi ja ühe ette võetud tööülesandega on järjekorda
    # logides ja SQL-tabelites lihtsam jälgida.
    worker_prefetch_multiplier=1,
    task_default_queue="celery",
)


def get_connection():
    """Loo PostgreSQL-i ühendus keskkonnamuutujate põhjal.

    Docker Compose annab samad väärtused nii `app` kui ka `worker` konteinerile.
    Ühenduse hoidmine koodist väljas kordab varasemate praktikumide `.env`
    faili kasutamise mõtet.
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )


def utc_now() -> datetime:
    """Tagasta praegune aeg koos ajavööndiga.

    Voogtöötluse näiteid on lihtsam mõista, kui ajatemplid on üheselt määratud.
    Koodis kasutame UTC-d (`Coordinated Universal Time`, koordineeritud
    maailmaaeg) ja PostgreSQL kuvab selle ajavööndiga ajatemplina.
    """
    return datetime.now(timezone.utc)


def as_payload(value):
    """Tagasta sündmuse `payload` Pythoni sõnastikuna.

    PostgreSQL-i `jsonb` väärtused jõuavad psycopg2 kaudu enamasti juba
    sõnastikuna. Kui väärtus tuleb tekstina, proovime seda JSON-ina lugeda.
    Kui see ei õnnestu, käsitleme sündmust vigasena ja kirjutame selle tabelisse
    `staging.bad_events`.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return json.loads(value)
    raise ValueError("Sündmuse `payload` ei ole loetav JSON-objekt.")


def require_text(payload: dict, field_name: str) -> str:
    """Loe sündmuse sisust kohustuslik tekstiväli."""
    value = payload.get(field_name)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Puudub välja `{field_name}` väärtus.")
    return str(value)


def require_int(payload: dict, field_name: str) -> int:
    """Loe sündmuse sisust kohustuslik positiivne täisarv."""
    value = payload.get(field_name)
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Väli `{field_name}` peab olema täisarv.") from exc
    if parsed <= 0:
        raise ValueError(f"Väli `{field_name}` peab olema suurem kui null.")
    return parsed


def require_decimal(payload: dict, field_name: str) -> Decimal:
    """Loe sündmuse sisust kohustuslik positiivne kümnendarv."""
    value = payload.get(field_name)
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Väli `{field_name}` peab olema arv.") from exc
    if parsed <= 0:
        raise ValueError(f"Väli `{field_name}` peab olema suurem kui null.")
    return parsed.quantize(Decimal("0.01"))


def log_task(cur, *, celery_task_id, event_id, status, message, started_at, finished_at):
    """Kirjuta üks worker'i töötluskatse tabelisse `monitoring.worker_task_log`.

    See tabel on õppijale loetav worker'i logi. Seda on lihtsam pärida kui
    konteineri toorlogi ning see teeb korduskatsed, vead ja vahele jäetud
    duplikaadid nähtavaks.
    """
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    cur.execute(
        """
        INSERT INTO monitoring.worker_task_log (
            celery_task_id,
            event_id,
            status,
            message,
            started_at,
            finished_at,
            duration_ms
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            celery_task_id,
            event_id,
            status,
            message,
            started_at,
            finished_at,
            duration_ms,
        ),
    )


@celery_app.task(bind=True, name="praktikum8.process_order_event")
def process_order_event(self, event_id: str) -> dict:
    """Töötle üks veebipoe tellimuse sündmus nähtavast sündmuste logist.

    Tööülesanne saab sisendiks ainult `event_id` väärtuse. Worker loeb päris
    sündmuse PostgreSQL-ist. Nii jääb Redis/Celery sõnum väikeseks ja sündmus
    ise on nähtav tabelis `stream.event_log`.

    Tööülesande voog on teadlikult väike ja jälgitav:

    - üks sündmus loetakse tabelist `stream.event_log`;
    - üks korrastatud rida kirjutatakse tabelisse `analytics.order_events`;
    - üks live-koond uueneb tabelis `analytics.sales_summary_live`;
    - iga töötluskatse kirjutatakse tabelisse `monitoring.worker_task_log`.
    """
    started_at = utc_now()
    celery_task_id = self.request.id

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Lukustame sündmuse rea ajaks, mil worker otsustab, mida teha.
                # See kaitseb rida olukorras, kus sama sündmus satub kogemata
                # mitu korda järjekorda.
                cur.execute(
                    """
                    SELECT event_type, event_time, payload, status
                    FROM stream.event_log
                    WHERE event_id = %s
                    FOR UPDATE
                    """,
                    (event_id,),
                )
                row = cur.fetchone()

                if row is None:
                    finished_at = utc_now()
                    log_task(
                        cur,
                        celery_task_id=celery_task_id,
                        event_id=event_id,
                        status="failed",
                        message="Sündmust ei leitud tabelist stream.event_log.",
                        started_at=started_at,
                        finished_at=finished_at,
                    )
                    return {"status": "failed", "reason": "event_not_found"}

                event_type, event_time, raw_payload, status = row

                if status == "processed":
                    # See on idempotentsuse kaitse. Tööülesanne võib saabuda
                    # rohkem kui üks kord, kuid sama sündmus ei tohi
                    # analüütika tulemust rohkem kui üks kord muuta.
                    finished_at = utc_now()
                    log_task(
                        cur,
                        celery_task_id=celery_task_id,
                        event_id=event_id,
                        status="skipped",
                        message="Sündmus oli juba töödeldud. Kordust ei lisatud.",
                        started_at=started_at,
                        finished_at=finished_at,
                    )
                    return {"status": "skipped", "reason": "already_processed"}

                # Märgime sündmuse töötluses olevaks. Kui worker hiljem katkeb,
                # aitavad olek ja worker'i logi näha, kuhu töö pooleli jäi.
                cur.execute(
                    """
                    UPDATE stream.event_log
                    SET status = 'processing'
                    WHERE event_id = %s
                    """,
                    (event_id,),
                )

                try:
                    # Kontrollime sündmuse sisu võimalikult selle koha lähedal,
                    # kus seda kasutatakse. Vigased sündmused on praktikumi osa:
                    # worker peab edasi töötama ja vigase sündmuse eraldi
                    # tabelisse kirjutama.
                    payload = as_payload(raw_payload)
                    if event_type != "order_created":
                        raise ValueError(f"Tundmatu sündmuse tüüp `{event_type}`.")

                    order_id = require_text(payload, "order_id")
                    store_id = require_text(payload, "store_id")
                    product_id = require_text(payload, "product_id")
                    quantity = require_int(payload, "quantity")
                    unit_price_eur = require_decimal(payload, "unit_price_eur")
                    total_amount_eur = (unit_price_eur * quantity).quantize(Decimal("0.01"))
                except ValueError as exc:
                    finished_at = utc_now()
                    cur.execute(
                        """
                        INSERT INTO staging.bad_events (
                            event_id,
                            event_type,
                            payload,
                            error_message
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (event_id) DO UPDATE
                        SET
                            payload = EXCLUDED.payload,
                            error_message = EXCLUDED.error_message,
                            recorded_at = now()
                        """,
                        (event_id, event_type, Json(raw_payload), str(exc)),
                    )
                    cur.execute(
                        """
                        UPDATE stream.event_log
                        SET
                            status = 'failed',
                            processed_at = %s,
                            error_message = %s
                        WHERE event_id = %s
                        """,
                        (finished_at, str(exc), event_id),
                    )
                    log_task(
                        cur,
                        celery_task_id=celery_task_id,
                        event_id=event_id,
                        status="failed",
                        message=str(exc),
                        started_at=started_at,
                        finished_at=finished_at,
                    )
                    return {"status": "failed", "reason": str(exc)}

                processed_at = utc_now()
                # Praktikum kasutab kaht minutit lihtsa vesimärgi-laadse
                # õppereeglina. See ei ole täismahus voogtöötluse vesimärk.
                is_late = (processed_at - event_time).total_seconds() > 120

                # Lisame korrastatud sündmuse. `ON CONFLICT DO NOTHING` on
                # teine idempotentsuse kaitse varasema olekukontrolli kõrval.
                cur.execute(
                    """
                    INSERT INTO analytics.order_events (
                        event_id,
                        order_id,
                        event_time,
                        processed_at,
                        store_id,
                        product_id,
                        quantity,
                        unit_price_eur,
                        total_amount_eur,
                        is_late
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                    RETURNING event_id
                    """,
                    (
                        event_id,
                        order_id,
                        event_time,
                        processed_at,
                        store_id,
                        product_id,
                        quantity,
                        unit_price_eur,
                        total_amount_eur,
                        is_late,
                    ),
                )
                inserted = cur.fetchone() is not None

                if inserted:
                    # Uuendame live-koondit ainult siis, kui korrastatud
                    # sündmuse rida lisati päriselt. Nii ei kasvata korduv
                    # tööülesanne koondit kaks korda.
                    cur.execute(
                        """
                        INSERT INTO analytics.sales_summary_live (
                            store_id,
                            product_id,
                            order_count,
                            total_quantity,
                            total_amount_eur,
                            last_event_time,
                            updated_at
                        )
                        VALUES (%s, %s, 1, %s, %s, %s, now())
                        ON CONFLICT (store_id, product_id) DO UPDATE
                        SET
                            order_count = analytics.sales_summary_live.order_count + 1,
                            total_quantity = analytics.sales_summary_live.total_quantity + EXCLUDED.total_quantity,
                            total_amount_eur = analytics.sales_summary_live.total_amount_eur + EXCLUDED.total_amount_eur,
                            last_event_time = GREATEST(
                                COALESCE(
                                    analytics.sales_summary_live.last_event_time,
                                    TIMESTAMPTZ '1900-01-01 00:00:00+00'
                                ),
                                EXCLUDED.last_event_time
                            ),
                            updated_at = now()
                        """,
                        (
                            store_id,
                            product_id,
                            quantity,
                            total_amount_eur,
                            event_time,
                        ),
                    )

                if is_late:
                    # Teeme hilinenud sündmused nähtavaks, et README-s olev
                    # sündmuse aja ja töötluse aja võrdlus oleks kontrollitav.
                    cur.execute(
                        """
                        INSERT INTO staging.late_events (
                            event_id,
                            event_time,
                            processed_at,
                            delay_seconds,
                            note
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO UPDATE
                        SET
                            processed_at = EXCLUDED.processed_at,
                            delay_seconds = EXCLUDED.delay_seconds,
                            recorded_at = now()
                        """,
                        (
                            event_id,
                            event_time,
                            processed_at,
                            Decimal(str(round((processed_at - event_time).total_seconds(), 2))),
                            "Sündmus töödeldi rohkem kui kaks minutit pärast event_time aega.",
                        ),
                    )

                # Sündmus on nüüd käsitletud. Ka duplikaadid jõuavad siia alles
                # pärast seda, kui põhilised analüütika tabelid on topeltkirjete
                # eest kaitstud.
                cur.execute(
                    """
                    UPDATE stream.event_log
                    SET
                        status = 'processed',
                        processed_at = %s,
                        error_message = NULL
                    WHERE event_id = %s
                    """,
                    (processed_at, event_id),
                )

                finished_at = utc_now()
                message = (
                    "Töödeldi ja lisati koondisse."
                    if inserted
                    else "Korduv tööülesanne. Koondit ei muudetud."
                )
                log_task(
                    cur,
                    celery_task_id=celery_task_id,
                    event_id=event_id,
                    status="processed" if inserted else "skipped",
                    message=message,
                    started_at=started_at,
                    finished_at=finished_at,
                )

                return {"status": "processed" if inserted else "skipped", "event_id": event_id}
    finally:
        conn.close()


if __name__ == "__main__":
    # Seda moodulit käivitab tavaliselt Celery.
    # Väike main-plokk teeb juhusliku otsekäivituse ohutuks.
    print("Käivita worker käsuga: celery -A scripts.celery_app worker --loglevel=INFO")
