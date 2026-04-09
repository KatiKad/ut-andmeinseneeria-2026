"""Kommenteeritud näide kahe allika ETL töövoost.

See fail aitab jälgida, kuidas üks lihtne ETL töövoog liigub kihiti:

- `staging` hoiab allikalähedasi andmeid;
- `intermediate` puhastab võtmed ja seob allikad;
- `analytics` hoiab lõpptabelit analüüsi jaoks.

Kui Python on sulle veel uus, loe faili ülevalt alla.
Iga funktsioon teeb ühe väikese sammu ja `main()` seob need sammud tervikuks.
"""

# `import` toob faili sisse teegid, mida me allpool kasutame.
import os

import psycopg2
import requests


# Suurte tähtedega nimi viitab tavaliselt konstandile:
# väärtusele, mida me programmi töö jooksul ei muuda.
API_URL = "https://jsonplaceholder.typicode.com/users"


def get_connection():
    """Loo andmebaasiühendus keskkonnamuutujate põhjal.

    Selle funktsiooni tulemus on connection-objekt, mille paneme hiljem
    muutujasse `conn`. Seda ühendust kasutame kõigi SQL-käskude jaoks.
    """

    # `os.environ.get("NIMI", "vaikimisi")` küsib väärtust keskkonnast.
    # Kui seda ei ole, kasutatakse paremal olevat vaikimisi väärtust.
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )


def fetch_api_users():
    """Andmete vastuvõtt: loe kasutajad API-st.

    Funktsioon tagastab loendi sõnastikest.
    Iga sõnastik esindab ühte kasutajat just nende väljadega,
    mida meil hiljem andmebaasi laadimiseks vaja on.
    """

    # `requests.get(...)` teeb veebipäringu ja tagastab Response-objekti.
    response = requests.get(API_URL, timeout=30)

    # Kui API vastas veakoodiga, katkestame töö kohe arusaadava veaga.
    response.raise_for_status()

    # `json()` muudab API vastuse Pythoni andmestruktuuriks.
    # Siin on tulemuseks loend, kus iga element on ühe kasutaja andmed.
    data = response.json()

    # Loome tühja loendi, kuhu hakkame puhastatud kujul kasutajaid lisama.
    users = []

    for item in data:
        users.append(
            {
                # Vasakul on meie enda valitud väljanimed.
                # Paremal võtame väärtused API vastusest.
                "user_id": item["id"],
                # `split()` ja `" ".join(...)` koos aitavad eemaldada
                # nimedest võimalikud liigsed tühikud.
                "full_name": " ".join(item["name"].split()),
                "username": item["username"],
                "email": item["email"],
                # API vastuses on osa andmeid pesastatud kujul.
                # See tähendab, et võtame kõigepealt `address` ja selle seest `city`.
                "city": item["address"]["city"],
                "company_name": item["company"]["name"],
            }
        )

    return users


def load_api_users(conn, api_users):
    """Laadimine staging kihti: salvesta API kasutajad tabelisse `staging.api_users`.

    Funktsioon saab kaks sisendit:
    - `conn` on andmebaasiühendus;
    - `api_users` on loend, mille tagastas `fetch_api_users()`.
    """

    # `with conn.cursor() as cur:` loob kursori, mille kaudu saame SQL-i käivitada.
    # `with` hoolitseb selle eest, et kursor suletakse ploki lõpus korrektselt.
    with conn.cursor() as cur:
        # `TRUNCATE` tühjendab tabeli kiiresti.
        # Nii jääb skript korduvkäivitamisel idempotentseks.
        cur.execute("TRUNCATE TABLE staging.api_users;")

        for user in api_users:
            cur.execute(
                """
                INSERT INTO staging.api_users (
                    user_id,
                    full_name,
                    username,
                    email,
                    city,
                    company_name,
                    loaded_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, NOW());
                """,
                (
                    # See tuppel peab olema samas järjekorras nagu `%s` kohad SQL-is.
                    user["user_id"],
                    user["full_name"],
                    user["username"],
                    user["email"],
                    user["city"],
                    user["company_name"],
                ),
            )

    # `commit()` kinnitab andmebaasimuudatused.
    conn.commit()


def count_status_rows(conn):
    """Tagasta, mitu staatusekirjet on tabelis `staging.user_status`.

    Selline väike kontroll aitab veenduda, et CSV laeti enne edukalt sisse.
    """

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM staging.user_status;")
        # `fetchone()` tagastab ühe rea. `COUNT(*)` puhul on see üks arv.
        return cur.fetchone()[0]


def count_intermediate_rows(conn):
    """Tagasta, mitu rida annab vaade `intermediate.user_profile_enriched`.

    See on lihtne viis kontrollida, et vaade oskab `staging` andmed
    omavahel kokku viia.
    """

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM intermediate.user_profile_enriched;")
        return cur.fetchone()[0]


def load_final_rows_from_intermediate(conn):
    """Laadimine analytics kihti: lae lõpptabel `intermediate` vaatest.

    Siin kasutatakse mustrit `INSERT ... SELECT ...`.
    See tähendab, et me ei pane ridu Pythonis ükshaaval kokku, vaid laseme
    andmebaasil endal vaate tulemuse lõpptabelisse kirjutada.
    """

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE analytics.user_profile;")

        # `INSERT ... SELECT` kopeerib vaate tulemuse otse lõpptabelisse.
        # `NOW()` lisab laadimise ajatempli jooksva hetke põhjal.
        cur.execute(
            """
            INSERT INTO analytics.user_profile (
                user_id,
                full_name,
                username,
                email,
                city,
                company_name,
                account_status,
                source_system,
                loaded_at
            )
            SELECT
                user_id,
                full_name,
                username,
                email,
                city,
                company_name,
                account_status,
                source_system,
                NOW()
            FROM intermediate.user_profile_enriched
            ORDER BY user_id;
            """
        )

        # `rowcount` ütleb, mitu rida eelmine SQL-käsk mõjutas.
        inserted_rows = cur.rowcount

    conn.commit()
    return inserted_rows


def main():
    """Käivita kogu töövoog õiges järjekorras.

    `main()` on selle faili põhitöövoog.
    Siin kutsume eelnevad funktsioonid ükshaaval välja ja prindime
    iga etapi järel lühikese vahekokkuvõtte.
    """

    # Siit algab kogu skripti peamine muutujate teekond:
    # get_connection() -> conn
    # fetch_api_users() -> api_users
    # count_intermediate_rows(conn) -> intermediate_rows
    # load_final_rows_from_intermediate(conn) -> inserted_rows
    conn = get_connection()

    # `try/finally` tähendab: proovi töö ära teha ja sule ühendus igal juhul.
    try:
        print("ETL etapp 1/3: Andmete vastuvõtt ja laadimine staging kihti")
        api_users = fetch_api_users()

        # `f"..."` on f-string.
        # See lubab panna muutuja väärtuse otse teksti sisse.
        print(f"- API-st tuli {len(api_users)} kasutajat.")
        load_api_users(conn, api_users)
        print(f"- Laadisin staging.api_users tabelisse {len(api_users)} rida.")
        print(f"- staging.user_status tabelis on {count_status_rows(conn)} staatusekirjet.")

        print("ETL etapp 2/3: Töötlus")
        intermediate_rows = count_intermediate_rows(conn)
        print(
            "- Intermediate vaade puhastas e-posti ja ühendas andmed "
            f"{intermediate_rows} kasutaja jaoks."
        )

        print("ETL etapp 3/3: Laadimine analytics kihti")
        inserted_rows = load_final_rows_from_intermediate(conn)
        print(
            f"- Laadisin analytics.user_profile tabelisse {inserted_rows} rida."
        )
        print("Valmis.")
    finally:
        conn.close()


# See plokk käivitab `main()` ainult siis, kui paneme selle faili otse jooksma.
if __name__ == "__main__":
    main()
