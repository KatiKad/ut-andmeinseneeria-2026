"""Andmekvaliteedi praktikumi väike orkestreerija.

See fail täidab 6. praktikumis sarnast rolli nagu
`scripts/orchestrate.py` täitis 4. praktikumis.

Sarnasus:

- mõlemad on käsupõhised;
- mõlemad aitavad töö jagada loogilisteks sammudeks;
- mõlemad jooksevad rakenduse konteineris, mitte andmebaasi konteineris.

Erinevus:

- 4. praktikum keskendus ajastamisele ja loogiliste kuupäevadele;
- 6. praktikum keskendub andmekvaliteedile ja andmehaldusele.

Seepärast on siin käsud ehitatud pigem tööetappide järgi:

- `refresh-dimensions`
- `load-orders`
- `run-quality`
- `build-mart`
- `add-metadata`
- `run-all`

Mõte on sama nagu eelmisel korral:
meil on üks väike töövooskript, mille samme saab käivitada eraldi
või vajadusel omavahel kombineerida.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

DEFAULT_FROM_DATE = date(2026, 3, 29)
DEFAULT_TO_DATE = date(2026, 4, 6)
PSQL_LOAD_DIMENSIONS_SQL = Path("scripts/00_load_dimension_snapshots.sql")
BUILD_DIMENSIONS_SQL = Path("scripts/01_build_dimensions.sql")
RUN_QUALITY_SQL = Path("scripts/02_run_quality_checks.sql")
BUILD_MART_SQL = Path("scripts/03_build_clean_mart.sql")
ADD_METADATA_SQL = Path("scripts/04_add_metadata.sql")
CHECK_RESULTS_SQL = Path("scripts/05_check_results.sql")


class UserFacingError(RuntimeError):
    """Viga, mida tahame õppijale näidata selge ja lühikese tekstina."""


def log(message: str) -> None:
    """Prindi üks lühike olekusõnum.

    Selles praktikumis kasutame lihtsat `print(...)` logimist.
    Nii on õppijal terminalis kohe näha, milline samm parajasti käib.
    """
    print(message, flush=True)


def get_connection():
    """Loo andmebaasiühendus keskkonnamuutujate põhjal.

    Sama skript töötab nii seetõttu, et ühenduse detailid ei ole koodi sisse kirjutatud.
    Need tulevad `.env` failist.
    """
    import psycopg2

    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )


def run_psql_file(sql_path: Path) -> None:
    """Käivita üks SQL-fail psql kliendiga.

    Oluline mõte:
    `psql` jookseb samas python-konteineris, kus jookseb see skript.
    See tähendab, et SQL-faili suhteline tee `scripts/...` on nähtav
    python-konteineri vaatest.
    """
    log(f"Käivitan SQL-faili {sql_path}.")
    subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-f", str(sql_path)],
        check=True,
    )


def fetch_one_value(conn, query: str):
    """Küsi andmebaasist üks väärtus.

    Seda kasutame lühikeste kontrollide jaoks, näiteks ridade arvu vaatamiseks.
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchone()[0]


def refresh_dimensions(conn) -> None:
    """Lae kuised snapshot-failid ja ehita neist SCD-dimensioonid.

    See on 6. praktikumi lähim vaste 4. praktikumi käsule `refresh-dimensions`.
    Ka siin on mõte sama:
    valmistame ette kirjeldavad tabelid, millele järgmised sammud saavad toetuda.
    """
    log("Alustan dimensioonide värskendamist.")
    run_psql_file(PSQL_LOAD_DIMENSIONS_SQL)
    run_psql_file(BUILD_DIMENSIONS_SQL)

    product_versions = fetch_one_value(
        conn,
        "SELECT COUNT(*) FROM intermediate.dim_products_scd;",
    )
    store_versions = fetch_one_value(
        conn,
        "SELECT COUNT(*) FROM intermediate.dim_stores_scd;",
    )
    log(
        "Dimensioonid on valmis: "
        f"{product_versions} tooteversiooni ja {store_versions} poeversiooni."
    )


def daterange(date_from: date, date_to: date):
    """Anna kuupäevad algusest lõpuni ükshaaval välja."""
    current = date_from
    while current <= date_to:
        yield current
        current += timedelta(days=1)


def get_source_api_url() -> str:
    """Tagasta kohaliku API põhiaadress.

    Hoiame selle loogika ühes kohas, et sama aadressi ei peaks
    mitmes funktsioonis uuesti kokku panema.
    """
    return os.environ.get("SOURCE_API_URL", "http://source-api:8016").rstrip("/")


def get_source_api_supported_range(source_api_url: str) -> tuple[date, date]:
    """Küsi kohalikult API-lt, milline kuupäevavahemik on lubatud.

    See aitab anda õppijale selge vea juba enne pikka laadimist.
    Nii ei jää terminali toore `HTTPError` virna.
    """
    import requests

    try:
        response = requests.get(f"{source_api_url}/health", timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise UserFacingError(
            "Kohaliku API tervisekontroll ebaõnnestus. "
            "Kontrolli, et teenus `source-api` töötab ja et `SOURCE_API_URL` viitab õigele aadressile."
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise UserFacingError(
            "Kohaliku API tervisekontroll ei tagastanud `JSON` vastust. "
            "Kontrolli, et `SOURCE_API_URL` viitab praktikumi allikateenusele."
        ) from exc

    try:
        available_from = date.fromisoformat(payload["available_from"])
        available_to = date.fromisoformat(payload["available_to"])
    except (KeyError, ValueError) as exc:
        raise UserFacingError(
            "Kohaliku API tervisekontroll ei tagastanud loetavat kuupäevavahemikku."
        ) from exc

    return available_from, available_to


def validate_requested_range(
    *,
    date_from: date,
    date_to: date,
    available_from: date,
    available_to: date,
) -> None:
    """Kontrolli, kas küsitud kuupäevavahemik mahub allika piiridesse."""
    if date_from > date_to:
        raise UserFacingError(
            "Alguskuupäev ei tohi olla lõppkuupäevast hilisem. "
            "Paranda käsu `--from-date` ja `--to-date` väärtused."
        )

    if date_from < available_from or date_to > available_to:
        raise UserFacingError(
            "Valitud kuupäevavahemik "
            f"{date_from.isoformat()} kuni {date_to.isoformat()} "
            "ei mahu kohaliku API toetatud vahemikku "
            f"{available_from.isoformat()} kuni {available_to.isoformat()}. "
            "Kasuta selle piiridesse jäävaid kuupäevi või muuda `.env` failis "
            "`SOURCE_START_DATE` ja `SOURCE_END_DATE` väärtusi ning käivita "
            "`docker compose up -d --build` uuesti."
        )


def fetch_orders_for_date(
    logical_date: date,
    *,
    source_api_url: str,
    available_from: date,
    available_to: date,
) -> list[dict]:
    """Küsi kohaliku API käest ühe päeva tellimused.

    Selle funktsiooni töö on ainult andmed kätte saada.
    Andmebaasi kirjutamine toimub hiljem eraldi sammus.
    Nii on tööjaotus selgem:

    - esmalt toome andmed allikast;
    - siis salvestame need staging-kihti.
    """
    import requests

    try:
        response = requests.get(
            f"{source_api_url}/orders",
            params={"date": logical_date.isoformat()},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise UserFacingError(
            "Kohaliku API päring ebaõnnestus kuupäeva "
            f"{logical_date.isoformat()} jaoks. "
            "Kontrolli, et teenus `source-api` töötab."
        ) from exc

    if not response.ok:
        server_message = ""
        try:
            payload = response.json()
            server_message = payload.get("error") or payload.get("message") or ""
        except ValueError:
            server_message = response.text.strip()

        message = (
            "Kohalik API ei tagastanud kuupäeva "
            f"{logical_date.isoformat()} kohta andmeid. "
            f"Toetatud kuupäevavahemik on {available_from.isoformat()} kuni {available_to.isoformat()}."
        )
        if server_message:
            message += f" API vastus oli: {server_message}"
        raise UserFacingError(message)

    try:
        payload = response.json()
    except ValueError as exc:
        raise UserFacingError(
            "Kohaliku API tellimuste päring ei tagastanud `JSON` vastust. "
            "Kontrolli, et kasutad praktikumi ootuspärast allikateenust."
        ) from exc

    if "orders" not in payload:
        raise UserFacingError(
            "Kohaliku API vastuses puudus väli `orders`. "
            "Kontrolli, et kasutad praktikumi ootuspärast allikateenust."
        )

    return payload["orders"]


def load_orders(conn, *, date_from: date, date_to: date) -> int:
    """Lae API-st tellimused staging-tabelisse.

    4. praktikumis oli keskne küsimus:
    "millise päeva töövoog parajasti jookseb?"

    Siin on küsimus veidi teistsugune:
    "millise kuupäevavahemiku toorandmed me kvaliteedikontrolli jaoks sisse toome?"

    Seepärast kasutame siin kuupäevavahemikku, mitte ainult ühte päeva.
    """
    source_api_url = get_source_api_url()
    available_from, available_to = get_source_api_supported_range(source_api_url)
    validate_requested_range(
        date_from=date_from,
        date_to=date_to,
        available_from=available_from,
        available_to=available_to,
    )

    total_rows = 0

    log(
        "Kohalik API toetab praegu kuupäevi "
        f"{available_from.isoformat()} kuni {available_to.isoformat()}."
    )

    # Selles praktikumis käsitleme `staging.orders_raw` tabelit kui
    # parajasti valitud töökomplekti.
    # Seepärast tühjendame tabeli enne laadimist täielikult ära.
    # Nii annab sama käsk sama vahemikuga käivitades alati sama tulemuse
    # ja ka väiksema või teistsuguse vahemiku laadimine ei jäta vanu ridu alles.
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE staging.orders_raw RESTART IDENTITY
            """
        )
    conn.commit()

    with conn.cursor() as cur:
        for logical_date in daterange(date_from, date_to):
            rows = fetch_orders_for_date(
                logical_date,
                source_api_url=source_api_url,
                available_from=available_from,
                available_to=available_to,
            )

            for row in rows:
                cur.execute(
                    """
                    INSERT INTO staging.orders_raw (
                        order_id,
                        order_date,
                        store_id,
                        product_id,
                        quantity,
                        unit_price_eur,
                        source_updated_at,
                        loaded_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        row.get("order_id"),
                        row["order_date"],
                        row.get("store_id"),
                        row.get("product_id"),
                        row.get("quantity"),
                        Decimal(str(row["unit_price_eur"])),
                        datetime.fromisoformat(row["source_updated_at"]),
                    ),
                )

            total_rows += len(rows)
            log(
                f"Laadisin kuupäeva {logical_date.isoformat()} kohta "
                f"{len(rows)} tellimuse rida."
            )

    conn.commit()
    log(f"Laadisin kokku {total_rows} tellimuse rida.")
    return total_rows


def run_quality(conn) -> None:
    """Käivita kvaliteedikontrollid ja näita lühikokkuvõtet."""
    log("Alustan kvaliteedikontrolle.")
    run_psql_file(RUN_QUALITY_SQL)

    clean_rows = fetch_one_value(conn, "SELECT COUNT(*) FROM quality.orders_clean;")
    rejected_rows = fetch_one_value(
        conn,
        "SELECT COUNT(DISTINCT staging_row_id) FROM quality.order_rule_results;",
    )
    log(
        "Kvaliteedikontrollid said valmis: "
        f"{clean_rows} puhast rida ja {rejected_rows} tagasi lükatud rida."
    )


def build_mart(conn) -> None:
    """Ehita puhas analüütikakiht kvaliteedikontrolli läbinud ridadest."""
    log("Ehitan puhastatud müügikoondi.")
    run_psql_file(BUILD_MART_SQL)

    mart_rows = fetch_one_value(
        conn,
        "SELECT COUNT(*) FROM analytics.daily_product_sales_clean;",
    )
    log(f"Puhastatud müügikoond on valmis: {mart_rows} koondrida.")


def add_metadata(conn) -> None:
    """Lisa metaandmed ja täida lihtne andmevara register."""
    log("Lisan tabelikirjeldused ja andmevara registri kirjed.")
    run_psql_file(ADD_METADATA_SQL)

    asset_rows = fetch_one_value(
        conn,
        "SELECT COUNT(*) FROM governance.data_asset_registry;",
    )
    log(f"Andmevara registris on nüüd {asset_rows} kirjet.")


def run_all(conn, *, date_from: date, date_to: date) -> None:
    """Käivita kogu 6. praktikumi põhirada ühe käsuga.

    See on 6. praktikumi lähim vaste mõttele "käivita terve töövoog".
    4. praktikumis oli selleks eri käskude kombinatsioon sõltuvalt sellest,
    kas töödeldi ühte päeva, ajalugu või ajastatud voogu.

    Siin on põhiküsimus teine:
    kas kogu kvaliteediahel on järjest läbi tehtud?
    """
    refresh_dimensions(conn)
    load_orders(conn, date_from=date_from, date_to=date_to)
    run_quality(conn)
    build_mart(conn)
    add_metadata(conn)


def parse_args() -> argparse.Namespace:
    """Loe käsurea argumendid.

    `argparse` aitab teha käsud kujul:

    - `refresh-dimensions`
    - `load-orders --from-date YYYY-MM-DD --to-date YYYY-MM-DD`
    - `run-quality`
    - `build-mart`
    - `add-metadata`
    - `run-all --from-date YYYY-MM-DD --to-date YYYY-MM-DD`

    Seda loogikat tasub võrrelda 4. praktikumi `subparsers` lahendusega.
    Ka seal tehti üks skript, millel oli mitu eri käsku.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "refresh-dimensions",
        help="Lae kuised snapshot-failid staging-kihti ja ehita SCD-dimensioonid.",
    )

    load_orders_parser = subparsers.add_parser(
        "load-orders",
        help="Lae kohaliku API tellimused staging-kihti valitud kuupäevavahemiku jaoks.",
    )
    load_orders_parser.add_argument("--from-date", default=DEFAULT_FROM_DATE, type=date.fromisoformat)
    load_orders_parser.add_argument("--to-date", default=DEFAULT_TO_DATE, type=date.fromisoformat)

    subparsers.add_parser(
        "run-quality",
        help="Käivita kvaliteedikontrollid ja loo puhaste ning vigaste ridade tabelid.",
    )

    subparsers.add_parser(
        "build-mart",
        help="Ehita puhastatud müügikoond quality-kihist analytics-kihti.",
    )

    subparsers.add_parser(
        "add-metadata",
        help="Lisa tabelikirjeldused ja täida andmevara register.",
    )

    run_all_parser = subparsers.add_parser(
        "run-all",
        help="Käivita kogu praktikumi põhirada järjest läbi.",
    )
    run_all_parser.add_argument("--from-date", default=DEFAULT_FROM_DATE, type=date.fromisoformat)
    run_all_parser.add_argument("--to-date", default=DEFAULT_TO_DATE, type=date.fromisoformat)

    subparsers.add_parser(
        "show-check-sql",
        help="Näita, kus asub koondpäringute fail.",
    )

    return parser.parse_args()


def main() -> None:
    """Käivita kasutaja valitud käsk."""
    args = parse_args()

    if args.command == "show-check-sql":
        print(CHECK_RESULTS_SQL)
        return

    conn = get_connection()
    try:
        if args.command == "refresh-dimensions":
            refresh_dimensions(conn)
            return

        if args.command == "load-orders":
            load_orders(
                conn,
                date_from=args.from_date,
                date_to=args.to_date,
            )
            return

        if args.command == "run-quality":
            run_quality(conn)
            return

        if args.command == "build-mart":
            build_mart(conn)
            return

        if args.command == "add-metadata":
            add_metadata(conn)
            return

        if args.command == "run-all":
            run_all(
                conn,
                date_from=args.from_date,
                date_to=args.to_date,
            )
            return
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except UserFacingError as exc:
        log(f"Viga: {exc}")
        raise SystemExit(1) from exc
