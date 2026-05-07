"""Kohalik API praktikumi tellimuste jaoks.

API annab iga kuupäeva kohta alati sama vastuse.
Nii saame andmekvaliteedi reegleid rahulikult läbi proovida.

Praktikumi jaoks on voos ka mõned tahtlikud vead:

- üks duplikaatne tellimuse ID;
- üks tundmatu toote ID;
- üks puuduva poe ID-ga rida;
- üks nullkogusega rida;
- üks selgelt vigase hinnaga rida.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8016"))
TALLINN_TZ = ZoneInfo(os.environ.get("TZ", "Europe/Tallinn"))
SOURCE_START_DATE = date.fromisoformat(os.environ.get("SOURCE_START_DATE", "2026-03-01"))
SOURCE_END_DATE = date.fromisoformat(os.environ.get("SOURCE_END_DATE", "2026-04-30"))
SEED_PREFIX = "praktikum-06-quality-source-api"

# Hoiame toodete kohta kahte kuuseisu.
# Nii saab sama toode või hind märtsi ja aprilli vahel muutuda.
MARCH_PRODUCTS = [
    {"product_id": "P-100", "base_price_eur": 24.90},
    {"product_id": "P-200", "base_price_eur": 34.50},
    {"product_id": "P-300", "base_price_eur": 49.00},
    {"product_id": "P-400", "base_price_eur": 6.80},
]

APRIL_PRODUCTS = [
    {"product_id": "P-100", "base_price_eur": 26.90},
    {"product_id": "P-200", "base_price_eur": 34.50},
    {"product_id": "P-300", "base_price_eur": 52.00},
    {"product_id": "P-400", "base_price_eur": 7.20},
    {"product_id": "P-500", "base_price_eur": 39.00},
]

# Sama mõte poodide kohta:
# aprillis võib lisanduda uus pood või muutuda olemasoleva poe kirjeldus.
MARCH_STORES = [
    {"store_id": "S-TLN"},
    {"store_id": "S-TRT"},
    {"store_id": "S-NRV"},
]

APRIL_STORES = [
    {"store_id": "S-TLN"},
    {"store_id": "S-TRT"},
    {"store_id": "S-NRV"},
    {"store_id": "S-PNU"},
]


def stable_int(seed: str, minimum: int, maximum: int) -> int:
    """Loo sisendi põhjal alati sama täisarv."""
    span = maximum - minimum + 1
    seeded_text = f"{SEED_PREFIX}|{seed}"
    value = int(sha256(seeded_text.encode("utf-8")).hexdigest()[:8], 16)
    return minimum + (value % span)


def get_product_catalog(logical_date: date) -> list[dict]:
    """Vali kuupäeva järgi õige tootekataloog."""
    if logical_date < date(2026, 4, 1):
        return MARCH_PRODUCTS
    return APRIL_PRODUCTS


def get_store_catalog(logical_date: date) -> list[dict]:
    """Vali kuupäeva järgi õige poodide loend."""
    if logical_date < date(2026, 4, 1):
        return MARCH_STORES
    return APRIL_STORES


def sort_orders_in_place(orders: list[dict]) -> None:
    """Sorteeri tellimused kuupäeva ja allika ajatembli järgi.

    Nii on API vastus brauseris ja laadimisskriptis lihtsamini jälgitav.
    Vajaduse korral kasutame sisemist `_event_no` välja viigiseisu lahendamiseks.
    """
    orders.sort(
        key=lambda order: (
            order["order_date"],
            order["source_updated_at"],
            order.get("_event_no", 0),
        )
    )


def build_orders(logical_date: date) -> list[dict]:
    """Ehita ühe päeva tellimused.

    4. praktikumi allikas oli rikkalikum:

    - päevane maht tuli normaaljaotusest;
    - aktiivsel äripäeval ei olnud kõik read kohe nähtavad;
    - olemas oli ka ajutise vea režiim `fail_once`.

    6. praktikumis hoiame allika lihtsamana, sest fookus on kvaliteedireeglitel.
    Siin on siiski kaks teadlikku sarnasust 4. praktikumi allikaga:

    - sama kuupäev annab alati sama vastuse;
    - vastus on ajaliselt sorteeritud.
    """
    product_catalog = get_product_catalog(logical_date)
    store_catalog = get_store_catalog(logical_date)
    order_count = stable_int(f"{logical_date.isoformat()}|count", 12, 18)

    raw_orders = []
    for order_no in range(1, order_count + 1):
        product = product_catalog[
            stable_int(
                f"{logical_date.isoformat()}|product|{order_no}",
                0,
                len(product_catalog) - 1,
            )
        ]
        store = store_catalog[
            stable_int(
                f"{logical_date.isoformat()}|store|{order_no}",
                0,
                len(store_catalog) - 1,
            )
        ]
        quantity = stable_int(f"{logical_date.isoformat()}|quantity|{order_no}", 1, 4)
        price_step = stable_int(f"{logical_date.isoformat()}|price_step|{order_no}", 0, 3)
        unit_price_eur = round(product["base_price_eur"] + (price_step * 0.5), 2)
        hour = stable_int(f"{logical_date.isoformat()}|hour|{order_no}", 8, 20)
        minute = stable_int(f"{logical_date.isoformat()}|minute|{order_no}", 0, 59)
        source_updated_at = datetime(
            logical_date.year,
            logical_date.month,
            logical_date.day,
            hour,
            minute,
            tzinfo=TALLINN_TZ,
        )

        raw_orders.append(
            {
                "order_date": logical_date.isoformat(),
                "store_id": store["store_id"],
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price_eur": unit_price_eur,
                "source_updated_at": source_updated_at.isoformat(),
                "_event_no": order_no,
            }
        )

    # Sorteerime esmalt toorsündmused, et lõplik vastus tuleks kronoloogiliselt.
    sort_orders_in_place(raw_orders)

    orders = []
    for order_no, raw_order in enumerate(raw_orders, start=1):
        orders.append(
            {
                "order_id": f"ORD-{logical_date.strftime('%Y%m%d')}-{order_no:03d}",
                "order_date": raw_order["order_date"],
                "store_id": raw_order["store_id"],
                "product_id": raw_order["product_id"],
                "quantity": raw_order["quantity"],
                "unit_price_eur": raw_order["unit_price_eur"],
                "source_updated_at": raw_order["source_updated_at"],
                "_event_no": raw_order["_event_no"],
            }
        )

    inject_known_quality_issues(logical_date, orders)
    sort_orders_in_place(orders)

    response_orders = []
    for order in orders:
        response_orders.append(
            {
                "order_id": order["order_id"],
                "order_date": order["order_date"],
                "store_id": order["store_id"],
                "product_id": order["product_id"],
                "quantity": order["quantity"],
                "unit_price_eur": order["unit_price_eur"],
                "source_updated_at": order["source_updated_at"],
            }
        )
    return response_orders


def inject_known_quality_issues(logical_date: date, orders: list[dict]) -> None:
    """Lisa voogu mõned sihilikud vead.

    Need vead on siia pandud selleks, et kvaliteedikontrollid päriselt midagi leiaksid.
    """
    # Iga valitud kuupäev tekitab ühe kindla tüüpi vea.
    # Nii on hiljem lihtne kontrollida, kas kvaliteedireeglid leiavad just need read üles.
    if logical_date == date(2026, 4, 1):
        orders[2]["product_id"] = "P-999"
    elif logical_date == date(2026, 4, 2):
        orders[4]["order_id"] = orders[3]["order_id"]
    elif logical_date == date(2026, 4, 3):
        orders[1]["store_id"] = ""
    elif logical_date == date(2026, 4, 4):
        orders[5]["quantity"] = 0
    elif logical_date == date(2026, 4, 5):
        orders[3]["unit_price_eur"] = 999.99


class RequestHandler(BaseHTTPRequestHandler):
    """Lihtne HTTP päringute töötleja."""

    server_version = "LocalQualityAPI/1.0"

    def _send_json(self, status_code: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_html(self, status_code: int, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _build_docs_page(self) -> str:
        """Ehita brauseris loetav API lühidokumentatsioon."""
        example_date = SOURCE_END_DATE
        return f"""<!doctype html>
<html lang="et">
  <head>
    <meta charset="utf-8">
    <title>Praktikum 6 kvaliteedi API</title>
    <style>
      body {{
        font-family: sans-serif;
        line-height: 1.5;
        margin: 2rem auto;
        max-width: 900px;
        padding: 0 1rem 3rem;
      }}
      code {{
        background: #f3f4f6;
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
      }}
      .card {{
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
      }}
      ul {{
        padding-left: 1.2rem;
      }}
    </style>
  </head>
  <body>
    <h1>Praktikum 6 kohalik tellimusallikas</h1>
    <p>See API on 4. praktikumi allikaga samast perest, kuid teadlikult lihtsam.</p>
    <p>Siin ei harjuta me ajastamist ega ajutiste vigade korduskatseid, vaid andmekvaliteedi kontrolli.</p>

    <div class="card">
      <h2>Praegune seis</h2>
      <ul>
        <li><strong>Andmeid alates:</strong> {SOURCE_START_DATE.isoformat()}</li>
        <li><strong>Andmeid kuni:</strong> {SOURCE_END_DATE.isoformat()}</li>
        <li><strong>Ajavöönd:</strong> {TALLINN_TZ.key}</li>
      </ul>
    </div>

    <div class="card">
      <h2>API teed</h2>

      <h3><code>GET /health</code></h3>
      <p>Tagastab teenuse oleku ja kuupäevavahemiku.</p>
      <p><a href="/health">Ava /health</a></p>

      <h3><code>GET /orders?date=YYYY-MM-DD</code></h3>
      <p>Tagastab ühe päeva tellimused.</p>
      <ul>
        <li>See on tee, mida kasutab praktikumi Pythoni skript.</li>
        <li>Vastus on sorteeritud välja <code>source_updated_at</code> järgi.</li>
      </ul>
      <p><a href="/orders?date={example_date.isoformat()}">Ava /orders näide</a></p>

      <h3><code>GET /api/orders?date=YYYY-MM-DD</code></h3>
      <p>See on eelmise teega samaväärne alias, et võrdlus 4. praktikumi API-ga oleks lihtsam.</p>
      <p><a href="/api/orders?date={example_date.isoformat()}">Ava /api/orders näide</a></p>
    </div>

    <div class="card">
      <h2>Tahtlikud kvaliteedivead</h2>
      <ul>
        <li><strong>2026-04-01:</strong> tundmatu toote ID</li>
        <li><strong>2026-04-02:</strong> duplikaatne tellimuse ID</li>
        <li><strong>2026-04-03:</strong> puuduva poe ID-ga rida</li>
        <li><strong>2026-04-04:</strong> nullkogusega rida</li>
        <li><strong>2026-04-05:</strong> selgelt vigane hind</li>
      </ul>
    </div>
  </body>
</html>
"""

    def log_message(self, fmt: str, *args) -> None:
        """Kirjuta serveri logiread terminali selgema kujuga."""
        print(f"[source-api] {self.address_string()} - {fmt % args}", flush=True)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/docs"}:
            self._send_html(200, self._build_docs_page())
            return

        if parsed.path == "/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "local-quality-source-api",
                    "available_from": SOURCE_START_DATE.isoformat(),
                    "available_to": SOURCE_END_DATE.isoformat(),
                    "orders_path": "/orders?date=YYYY-MM-DD",
                    "docs_path": "/docs",
                },
            )
            return

        # Toetame kahte teed:
        # `/orders` on praktikumi põhiraja tee
        # ja `/api/orders` aitab seda allikat mugavamalt võrrelda 4. praktikumi API-ga.
        if parsed.path in {"/orders", "/api/orders"}:
            query = parse_qs(parsed.query)
            logical_date_text = query.get("date", [None])[0]
            if logical_date_text is None:
                self._send_json(400, {"error": "Kasuta kuju /orders?date=YYYY-MM-DD"})
                return

            try:
                logical_date = date.fromisoformat(logical_date_text)
            except ValueError:
                self._send_json(400, {"error": "Kuupäev peab olema kujul YYYY-MM-DD"})
                return

            if logical_date < SOURCE_START_DATE or logical_date > SOURCE_END_DATE:
                self._send_json(
                    400,
                    {
                        "error": (
                            "Kuupäev peab jääma vahemikku "
                            f"{SOURCE_START_DATE.isoformat()} kuni {SOURCE_END_DATE.isoformat()}"
                        )
                    },
                )
                return

            orders = build_orders(logical_date)
            self._send_json(
                200,
                {
                    "logical_date": logical_date.isoformat(),
                    "row_count": len(orders),
                    "sorted_by": ["order_date", "source_updated_at"],
                    "orders": orders,
                },
            )
            return

        self._send_json(404, {"error": "Sellist teed ei ole olemas."})


def main() -> None:
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(
        f"[source-api] Käivitus aadressil http://{HOST}:{PORT} "
        f"(andmed {SOURCE_START_DATE.isoformat()} kuni {SOURCE_END_DATE.isoformat()})",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
