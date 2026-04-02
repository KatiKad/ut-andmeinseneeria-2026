"""
Ulesanne 3 lahendus: Python ETL - OLTP allikast star schemasse
"""

import csv
import os
from datetime import datetime

import psycopg2


CSV_PATH = "/data/source_sales.csv"

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "dbname": os.environ.get("POSTGRES_DB", "praktikum"),
    "user": os.environ.get("POSTGRES_USER", "praktikum"),
    "password": os.environ.get("POSTGRES_PASSWORD", "praktikum"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def extract(csv_path: str) -> list[dict]:
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def transform_dimensions(rows: list[dict]) -> dict:
    dates_set = {}
    stores_set = {}
    products_set = {}
    customers_set = {}
    payments_set = set()

    for row in rows:
        # Kuupaevad
        d = row["order_date"]
        if d not in dates_set:
            dt = datetime.strptime(d, "%Y-%m-%d")
            dates_set[d] = {
                "date_key": int(dt.strftime("%Y%m%d")),
                "full_date": d,
                "year": dt.year,
                "quarter": (dt.month - 1) // 3 + 1,
                "month": dt.month,
                "day": dt.day,
                "day_of_week": dt.strftime("%A"),
                "day_of_year": dt.timetuple().tm_yday,
                "week_of_year": dt.isocalendar()[1],
                "month_name": dt.strftime("%B"),
                "is_weekend": dt.isoweekday() in (6, 7),
            }

        # Poed
        sn = row["store_name"]
        if sn not in stores_set:
            stores_set[sn] = {
                "store_name": sn,
                "city": row["store_city"],
                "region": row["store_region"],
            }

        # Tooted
        pn = row["product_name"]
        if pn not in products_set:
            products_set[pn] = {
                "product_name": pn,
                "category": row["product_category"],
                "brand": row["product_brand"],
            }

        # Kliendid
        cid = int(row["customer_id"])
        if cid not in customers_set:
            parts = row["customer_name"].split(" ", 1)
            customers_set[cid] = {
                "customer_id": cid,
                "first_name": parts[0],
                "last_name": parts[1] if len(parts) > 1 else "",
                "segment": row["customer_segment"],
                "city": row["customer_city"],
            }

        # Makseviisid
        payments_set.add(row["payment_type"])

    return {
        "dates": sorted(dates_set.values(), key=lambda x: x["full_date"]),
        "stores": sorted(stores_set.values(), key=lambda x: x["store_name"]),
        "products": sorted(products_set.values(), key=lambda x: x["product_name"]),
        "customers": sorted(customers_set.values(), key=lambda x: x["customer_id"]),
        "payments": [{"payment_type": pt} for pt in sorted(payments_set)],
    }


def transform_facts(rows: list[dict]) -> list[dict]:
    facts = []
    for row in rows:
        facts.append(
            {
                "order_date": row["order_date"],
                "store_name": row["store_name"],
                "product_name": row["product_name"],
                "customer_id": int(row["customer_id"]),
                "payment_type": row["payment_type"],
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
                "total_amount": float(row["total_amount"]),
            }
        )
    return facts


def load(conn, dimensions: dict, facts: list[dict]) -> int:
    cur = conn.cursor()

    # Idempotentsus: tuhjenda tabelid
    cur.execute("TRUNCATE TABLE FactSales RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE DimDate RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE DimStore RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE DimProduct RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE DimCustomer RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE DimPayment RESTART IDENTITY CASCADE")

    # Laadi DimDate
    for d in dimensions["dates"]:
        cur.execute(
            "INSERT INTO DimDate (DateKey, FullDate, Year, Quarter, Month, Day, DayOfWeek, DayOfYear, WeekOfYear, MonthName, IsWeekend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (d["date_key"], d["full_date"], d["year"], d["quarter"], d["month"], d["day"], d["day_of_week"], d["day_of_year"], d["week_of_year"], d["month_name"], d["is_weekend"]),
        )

    # Laadi DimStore
    for s in dimensions["stores"]:
        cur.execute(
            "INSERT INTO DimStore (StoreName, City, Region) VALUES (%s, %s, %s)",
            (s["store_name"], s["city"], s["region"]),
        )

    # Laadi DimProduct
    for p in dimensions["products"]:
        cur.execute(
            "INSERT INTO DimProduct (ProductName, Category, Brand) VALUES (%s, %s, %s)",
            (p["product_name"], p["category"], p["brand"]),
        )

    # Laadi DimCustomer
    for c in dimensions["customers"]:
        cur.execute(
            "INSERT INTO DimCustomer (CustomerID, FirstName, LastName, Segment, City) VALUES (%s, %s, %s, %s, %s)",
            (c["customer_id"], c["first_name"], c["last_name"], c["segment"], c["city"]),
        )

    # Laadi DimPayment
    for pm in dimensions["payments"]:
        cur.execute(
            "INSERT INTO DimPayment (PaymentType) VALUES (%s)",
            (pm["payment_type"],),
        )

    conn.commit()

    # Loe surrogate key'd tagasi
    cur.execute("SELECT DateKey, FullDate FROM DimDate")
    date_keys = {str(row[1]): row[0] for row in cur.fetchall()}

    cur.execute("SELECT StoreKey, StoreName FROM DimStore")
    store_keys = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT ProductKey, ProductName FROM DimProduct")
    product_keys = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT CustomerKey, CustomerID FROM DimCustomer")
    customer_keys = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT PaymentKey, PaymentType FROM DimPayment")
    payment_keys = {row[1]: row[0] for row in cur.fetchall()}

    # Laadi FactSales
    rows_loaded = 0
    for f in facts:
        cur.execute(
            """INSERT INTO FactSales (DateKey, StoreKey, ProductKey, CustomerKey, PaymentKey, Quantity, UnitPrice, TotalAmount)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                date_keys[f["order_date"]],
                store_keys[f["store_name"]],
                product_keys[f["product_name"]],
                customer_keys[f["customer_id"]],
                payment_keys[f["payment_type"]],
                f["quantity"],
                f["unit_price"],
                f["total_amount"],
            ),
        )
        rows_loaded += 1

    conn.commit()
    cur.close()
    return rows_loaded


def ensure_etl_log_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS etl_log (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds NUMERIC(10,2),
            rows_loaded INT,
            status VARCHAR(20),
            error_message TEXT
        )
    """)
    conn.commit()
    cur.close()


def log_etl_run(conn, start_time, end_time, rows_loaded, status, error_message=None):
    duration = round((end_time - start_time).total_seconds(), 2)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO etl_log (start_time, end_time, duration_seconds, rows_loaded, status, error_message)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (start_time, end_time, duration, rows_loaded, status, error_message),
    )
    conn.commit()
    cur.close()


def main():
    print("=" * 50)
    print("ETL: OLTP allikas -> Star Schema")
    print("=" * 50)

    conn = get_connection()
    ensure_etl_log_table(conn)
    start_time = datetime.now()
    rows_loaded = 0

    try:
        print("\n[1/4] EXTRACT: loen CSV faili...")
        raw_rows = extract(CSV_PATH)
        print(f"      Loetud {len(raw_rows)} rida")

        print("\n[2/4] TRANSFORM: eraldan dimensioonid...")
        dimensions = transform_dimensions(raw_rows)
        for dim_name, dim_rows in dimensions.items():
            print(f"      {dim_name}: {len(dim_rows)} unikaalset kirjet")

        print("\n[3/4] TRANSFORM: valmistan ette faktid...")
        facts = transform_facts(raw_rows)
        print(f"      {len(facts)} faktirida")

        print("\n[4/4] LOAD: laadin andmebaasi...")
        rows_loaded = load(conn, dimensions, facts)
        print(f"      Laaditud {rows_loaded} faktirida")

        end_time = datetime.now()
        log_etl_run(conn, start_time, end_time, rows_loaded, "success")

        # Kontroll
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM FactSales")
        print(f"\n      Kontroll: FactSales tabelis {cur.fetchone()[0]} rida")
        cur.execute("SELECT COUNT(*) FROM DimCustomer")
        print(f"      Kontroll: DimCustomer tabelis {cur.fetchone()[0]} rida")
        cur.close()

        print(f"\nETL VALMIS! Kestus: {(end_time - start_time).total_seconds():.2f}s")

    except Exception as e:
        end_time = datetime.now()
        log_etl_run(conn, start_time, end_time, rows_loaded, "error", str(e))
        print(f"\nETL VIGA: {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
