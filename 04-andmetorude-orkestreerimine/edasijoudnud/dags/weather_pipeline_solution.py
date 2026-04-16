"""
European Weather Pipeline — Täidetud lahendus (kõik ülesanded)

Sisaldab:
- Demo: riikide ja ilmaandmete laadimine, dbt, valideerimine
- Ülesanne 1: ISS ilmaandmed (viitepõhine XCom muster)
- Ülesanne 2: Valikumuster (@task.branch) ja retry
- Ülesanne 3: Dynamic Task Mapping (.expand())
"""

from datetime import timedelta

import pendulum

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

# Pealinnad, mille ilmaandmeid pärime
CITIES = [
    {"name": "Tallinn", "country_code": "EST", "lat": 59.44, "lon": 24.75},
    {"name": "Helsinki", "country_code": "FIN", "lat": 60.17, "lon": 24.94},
    {"name": "Riga", "country_code": "LVA", "lat": 56.95, "lon": 24.11},
    {"name": "Stockholm", "country_code": "SWE", "lat": 59.33, "lon": 18.07},
    {"name": "Warsaw", "country_code": "POL", "lat": 52.23, "lon": 21.01},
]


@dag(
    dag_id="weather_pipeline_complete",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 3, 25, tz="UTC"),
    catchup=False,
    tags=["weather", "praktikum", "lahendus"],
)
def weather_pipeline_complete():

    # -------------------------------------------------------------------
    # Ülesanne 2: Valikumuster — @task.branch
    # -------------------------------------------------------------------

    @task.branch
    def choose_countries_path():
        """
        Kontrollib, kas riikide andmed on juba laaditud.
        Tagastab valitud haru task_id.
        """
        from contextlib import closing

        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id="analytics_db")
        with closing(hook.get_conn()) as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM staging.countries_raw")
            count = cur.fetchone()[0]

        if count == 0:
            return "extract_countries"
        print(f"Riikide andmed on juba laaditud ({count} rida), jätame vahele")
        return "run_dbt"

    @task
    def extract_countries(ds=None) -> str:
        """
        Pärib riikide metaandmed REST Countries API-st ja salvestab faili.
        Tagastab XCom-i kaudu ainult failitee.
        """
        import json
        import urllib.parse
        import urllib.request
        from datetime import date

        params = urllib.parse.urlencode({
            "codes": ",".join(c["country_code"] for c in CITIES),
            "fields": "cca3,name,capital,latlng,population,area,currencies",
        })
        url = f"https://restcountries.com/v3.1/alpha?{params}"

        req = urllib.request.Request(
            url, headers={"User-Agent": "Airflow-Praktikum/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        countries = []
        for item in data:
            currency_code = ""
            currency_name = ""
            if item.get("currencies"):
                first_key = next(iter(item["currencies"]))
                currency_code = first_key
                currency_name = item["currencies"][first_key].get("name", "")

            countries.append(
                {
                    "country_code": item["cca3"],
                    "country_name": item["name"]["common"],
                    "capital": item.get("capital", [None])[0],
                    "latitude": item["latlng"][0] if item.get("latlng") else None,
                    "longitude": item["latlng"][1] if item.get("latlng") else None,
                    "population": item.get("population"),
                    "area_km2": item.get("area"),
                    "currency_code": currency_code,
                    "currency_name": currency_name,
                }
            )

        path = f"/tmp/countries_{ds or date.today().isoformat()}.json"
        with open(path, "w") as f:
            json.dump(countries, f)
        print(f"Laeti {len(countries)} riiki, salvestatud: {path}")
        return path

    @task
    def load_staging_countries(file_path: str) -> int:
        """
        Loeb riikide andmed failist ja laeb staging.countries_raw tabelisse.
        UPSERT tagab idempotentsuse.
        """
        import json
        from contextlib import closing

        from airflow.providers.postgres.hooks.postgres import PostgresHook

        with open(file_path) as f:
            countries = json.load(f)

        hook = PostgresHook(postgres_conn_id="analytics_db")
        with closing(hook.get_conn()) as conn, conn, conn.cursor() as cur:
            for c in countries:
                cur.execute(
                    """
                    INSERT INTO staging.countries_raw
                        (country_code, country_name, capital, latitude, longitude,
                         population, area_km2, currency_code, currency_name, loaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (country_code) DO UPDATE SET
                        country_name = EXCLUDED.country_name,
                        capital = EXCLUDED.capital,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        population = EXCLUDED.population,
                        area_km2 = EXCLUDED.area_km2,
                        currency_code = EXCLUDED.currency_code,
                        currency_name = EXCLUDED.currency_name,
                        loaded_at = NOW()
                    """,
                    (
                        c["country_code"],
                        c["country_name"],
                        c["capital"],
                        c["latitude"],
                        c["longitude"],
                        c["population"],
                        c["area_km2"],
                        c["currency_code"],
                        c["currency_name"],
                    ),
                )

        print(f"Laaditud {len(countries)} riiki staging tabelisse")
        return len(countries)

    # -------------------------------------------------------------------
    # Ülesanne 3: Dynamic Task Mapping — get_cities + extract_single_city_weather
    # -------------------------------------------------------------------

    @task
    def get_cities() -> list:
        """Tagastab linnade nimekirja dünaamiliseks kaardistamiseks."""
        return CITIES

    # Ülesanne 2: Retry lisatud; Ülesanne 3: võtab vastu ühe linna
    @task(retries=3, retry_delay=timedelta(minutes=1))
    def extract_single_city_weather(city: dict, ds=None) -> str:
        """
        Pärib ilmaandmed ühele linnale Open-Meteo Archive API-st ja salvestab faili.
        Tagastab XCom-i kaudu ainult failitee.

        city — linna dict (name, country_code, lat, lon).
        ds   — Airflow süstib loogilise kuupäeva stringina (nt "2025-04-01").
        """
        import json
        import urllib.parse
        import urllib.request
        from datetime import date

        query_date = ds if ds else date.today().isoformat()

        params = urllib.parse.urlencode({
            "latitude": city["lat"],
            "longitude": city["lon"],
            "start_date": query_date,
            "end_date": query_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "Europe/Tallinn",
        })
        url = f"https://archive-api.open-meteo.com/v1/archive?{params}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Airflow-Praktikum/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        daily = data.get("daily", {})
        weather_row = None
        if daily and daily.get("time"):
            weather_row = {
                "city_name": city["name"],
                "country_code": city["country_code"],
                "latitude": city["lat"],
                "longitude": city["lon"],
                "observation_date": daily["time"][0],
                "temp_max_c": daily["temperature_2m_max"][0],
                "temp_min_c": daily["temperature_2m_min"][0],
                "precipitation_mm": daily["precipitation_sum"][0],
                "wind_speed_max_kmh": daily["wind_speed_10m_max"][0],
            }

        path = f"/tmp/weather_{city['name'].lower()}_{query_date}.json"
        with open(path, "w") as f:
            json.dump(weather_row, f)
        print(f"Laeti ilmaandmed linnale {city['name']} ({query_date}), salvestatud: {path}")
        return path

    @task
    def load_staging_weather(file_path: str) -> int:
        """
        Loeb ilmaandmed failist ja laeb staging.weather_raw tabelisse.
        UPSERT (country_code + observation_date) tagab idempotentsuse.

        Ülesanne 3: file_path võib olla ka list[str] (.expand() korral).
        """
        import json
        from contextlib import closing

        from airflow.providers.postgres.hooks.postgres import PostgresHook

        # Ülesanne 3: .expand() annab LazyXComSequence (või list) failiteedest
        paths = [file_path] if isinstance(file_path, str) else list(file_path)

        weather_rows = []
        for p in paths:
            with open(p) as f:
                data = json.load(f)
            if isinstance(data, list):
                weather_rows.extend(data)
            elif isinstance(data, dict):
                weather_rows.append(data)

        hook = PostgresHook(postgres_conn_id="analytics_db")
        with closing(hook.get_conn()) as conn, conn, conn.cursor() as cur:
            for w in weather_rows:
                cur.execute(
                    """
                    INSERT INTO staging.weather_raw
                        (city_name, country_code, latitude, longitude,
                         observation_date, temp_max_c, temp_min_c,
                         precipitation_mm, wind_speed_max_kmh, loaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (country_code, observation_date) DO UPDATE SET
                        city_name = EXCLUDED.city_name,
                        temp_max_c = EXCLUDED.temp_max_c,
                        temp_min_c = EXCLUDED.temp_min_c,
                        precipitation_mm = EXCLUDED.precipitation_mm,
                        wind_speed_max_kmh = EXCLUDED.wind_speed_max_kmh,
                        loaded_at = NOW()
                    """,
                    (
                        w["city_name"],
                        w["country_code"],
                        w["latitude"],
                        w["longitude"],
                        w["observation_date"],
                        w["temp_max_c"],
                        w["temp_min_c"],
                        w["precipitation_mm"],
                        w["wind_speed_max_kmh"],
                    ),
                )

        print(f"Laaditud {len(weather_rows)} ilmarida staging tabelisse")
        return len(weather_rows)

    # -------------------------------------------------------------------
    # Ülesanne 1: ISS ilmaandmed — viitepõhine XCom muster
    # -------------------------------------------------------------------

    @task(retries=3, retry_delay=timedelta(seconds=5), retry_exponential_backoff=True)
    def extract_iss_position(ds=None) -> str:
        """
        Pärib ISS hetkeasukoha ja salvestab faili.
        Tagastab XCom-i kaudu ainult failitee.
        """
        import json
        import urllib.request
        from datetime import date

        url = "http://api.open-notify.org/iss-now.json"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Airflow-Praktikum/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        position = {
            "latitude": float(data["iss_position"]["latitude"]),
            "longitude": float(data["iss_position"]["longitude"]),
            "timestamp": data["timestamp"],
        }

        path = f"/tmp/iss_position_{ds or date.today().isoformat()}.json"
        with open(path, "w") as f:
            json.dump(position, f)
        print(f"ISS asukoht: lat={position['latitude']}, lon={position['longitude']}, salvestatud: {path}")
        return path

    @task
    def extract_iss_weather(position_path: str, ds=None) -> str:
        """
        Loeb ISS positsiooni failist ja pärib Open-Meteo hetkeilma.
        Salvestab tulemuse faili ja tagastab failitee.
        Kasutab forecast (mitte archive) API-t, sest ISS positsioon on reaalajas.
        """
        import json
        import urllib.parse
        import urllib.request
        from datetime import date

        with open(position_path) as f:
            position = json.load(f)

        params = urllib.parse.urlencode({
            "latitude": position["latitude"],
            "longitude": position["longitude"],
            "current": "temperature_2m,wind_speed_10m,weather_code",
        })
        url = f"https://api.open-meteo.com/v1/forecast?{params}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Airflow-Praktikum/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        current = data.get("current", {})
        result = {
            "iss_latitude": position["latitude"],
            "iss_longitude": position["longitude"],
            "timestamp": position["timestamp"],
            "temp_c": current.get("temperature_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
        }

        path = f"/tmp/iss_weather_{ds or date.today().isoformat()}.json"
        with open(path, "w") as f:
            json.dump(result, f)
        print(f"ISS ilm: temp={result['temp_c']}°C, tuul={result['wind_speed_kmh']} km/h, salvestatud: {path}")
        return path

    @task
    def load_staging_iss_weather(weather_path: str) -> int:
        """
        Loeb ISS ilmaandmed failist ja laeb staging.iss_weather_raw tabelisse.
        UPSERT (observation_time) tagab idempotentsuse.
        """
        import json
        from contextlib import closing
        from datetime import datetime as dt

        from airflow.providers.postgres.hooks.postgres import PostgresHook

        with open(weather_path) as f:
            iss_weather = json.load(f)

        observation_time = dt.utcfromtimestamp(iss_weather["timestamp"])

        hook = PostgresHook(postgres_conn_id="analytics_db")
        with closing(hook.get_conn()) as conn, conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO staging.iss_weather_raw
                    (observation_time, iss_latitude, iss_longitude,
                     temp_c, wind_speed_kmh, weather_code, loaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (observation_time) DO UPDATE SET
                    iss_latitude = EXCLUDED.iss_latitude,
                    iss_longitude = EXCLUDED.iss_longitude,
                    temp_c = EXCLUDED.temp_c,
                    wind_speed_kmh = EXCLUDED.wind_speed_kmh,
                    weather_code = EXCLUDED.weather_code,
                    loaded_at = NOW()
                """,
                (
                    observation_time,
                    iss_weather["iss_latitude"],
                    iss_weather["iss_longitude"],
                    iss_weather["temp_c"],
                    iss_weather["wind_speed_kmh"],
                    iss_weather["weather_code"],
                ),
            )

        print(f"ISS ilmaandmed laaditud (vaatlusaeg: {observation_time})")
        return 1

    # -------------------------------------------------------------------
    # @task.virtualenv valideerimine
    # -------------------------------------------------------------------

    @task.virtualenv(requirements=["duckdb==1.3.0"])
    def validate_with_duckdb() -> dict:
        """Andmekvaliteedi kontroll DuckDB-ga."""
        import os

        import duckdb

        host = os.environ.get("POSTGRES_HOST", "analytics-db")
        port = os.environ.get("POSTGRES_PORT", "5432")
        user = os.environ.get("POSTGRES_USER", "praktikum")
        password = os.environ.get("POSTGRES_PASSWORD", "praktikum")
        dbname = os.environ.get("POSTGRES_DB", "praktikum")

        conn = duckdb.connect()
        conn.execute("INSTALL postgres; LOAD postgres;")
        conn.execute(
            f"""
            ATTACH 'host={host} port={port} dbname={dbname} user={user} password={password}'
            AS pg (TYPE postgres, READ_ONLY)
            """
        )

        weather_count = conn.execute(
            "SELECT COUNT(*) FROM pg.staging.weather_raw"
        ).fetchone()[0]
        countries_count = conn.execute(
            "SELECT COUNT(*) FROM pg.staging.countries_raw"
        ).fetchone()[0]
        null_temps = conn.execute(
            "SELECT COUNT(*) FROM pg.staging.weather_raw WHERE temp_max_c IS NULL"
        ).fetchone()[0]

        result = {
            "weather_rows": weather_count,
            "countries_rows": countries_count,
            "null_temperatures": null_temps,
            "status": "OK" if null_temps == 0 else "WARNING",
        }
        print(f"Valideerimise tulemus: {result}")
        conn.close()
        return result

    # -------------------------------------------------------------------
    # dbt käivitamine BashOperator-iga
    # -------------------------------------------------------------------

    dbt_run = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "dbt build"
            " --project-dir /opt/airflow/dbt_project"
            " --profiles-dir /opt/airflow/dbt_project"
        ),
        # Ülesanne 2: trigger_rule lubab käivituda ka siis,
        # kui branch jättis riikide laadimise vahele
        trigger_rule="none_failed_min_one_success",
    )

    dbt_test = BashOperator(
        task_id="test_dbt",
        bash_command=(
            "dbt test"
            " --project-dir /opt/airflow/dbt_project"
            " --profiles-dir /opt/airflow/dbt_project"
        ),
    )

    # -------------------------------------------------------------------
    # Sõltuvuste defineerimine
    # -------------------------------------------------------------------

    # Ülesanne 2: Valikumuster — branch otsustab, kas laadida riigid
    branch = choose_countries_path()
    countries_path = extract_countries()
    countries_loaded = load_staging_countries(countries_path)
    branch >> countries_path
    countries_loaded >> dbt_run

    # Ülesanne 3: Dynamic Task Mapping — iga linna kohta eraldi ülesanne
    cities = get_cities()
    weather_paths = extract_single_city_weather.expand(city=cities)
    weather_loaded = load_staging_weather(weather_paths)
    weather_loaded >> dbt_run

    # Ülesanne 1: ISS ilmaandmed (paralleelselt teiste harudega)
    iss_position_path = extract_iss_position()
    iss_weather_path = extract_iss_weather(iss_position_path)
    iss_loaded = load_staging_iss_weather(iss_weather_path)
    iss_loaded >> dbt_run

    # dbt ja valideerimine
    dbt_run >> dbt_test >> validate_with_duckdb()

    # Ülesanne 2: branch peab teadma ka run_dbt-st (vahele jätmise korral)
    branch >> dbt_run


weather_pipeline_complete()
