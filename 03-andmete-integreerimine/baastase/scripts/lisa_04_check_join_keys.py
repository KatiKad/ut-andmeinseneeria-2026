"""Kontrolli, kas staging tabelite võtmed sobituvad."""

import os

import psycopg2
from psycopg2 import sql


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "praktikum"),
        password=os.environ.get("DB_PASSWORD", "praktikum"),
        dbname=os.environ.get("DB_NAME", "praktikum"),
    )


def split_relation_name(relation_name):
    schema_name, table_name = relation_name.split(".", maxsplit=1)
    return schema_name, table_name


def relation_exists(conn, relation_name):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s);", (relation_name,))
        return cur.fetchone()[0] is not None


def fetch_normalized_keys(conn, relation_name, key_column):
    schema_name, table_name = split_relation_name(relation_name)

    query = sql.SQL(
        """
        SELECT DISTINCT LOWER(TRIM({key_column}::text)) AS key_value
        FROM {schema_name}.{table_name}
        WHERE {key_column} IS NOT NULL
        ORDER BY key_value;
        """
    ).format(
        schema_name=sql.Identifier(schema_name),
        table_name=sql.Identifier(table_name),
        key_column=sql.Identifier(key_column),
    )

    with conn.cursor() as cur:
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]


def compare_key_sets(left_keys, right_keys):
    left_key_set = set(left_keys)
    right_key_set = set(right_keys)

    return {
        "matched_keys": sorted(left_key_set & right_key_set),
        "left_only_keys": sorted(left_key_set - right_key_set),
        "right_only_keys": sorted(right_key_set - left_key_set),
    }


def print_check_keys(
    conn,
    source_a,
    source_b,
    key,
    label_a,
    label_b,
):
    left_keys = fetch_normalized_keys(conn, source_a, key)
    right_keys = fetch_normalized_keys(conn, source_b, key)
    comparison = compare_key_sets(left_keys, right_keys)

    print(f"- Võrdlus: {label_a} ja {label_b}")
    print(f"- Sobitunud e-posti võtmeid: {len(comparison['matched_keys'])}")
    print(
        f"- {label_a} poolel ilma {label_b} vasteta: "
        f"{len(comparison['left_only_keys'])}"
    )
    for key_value in comparison["left_only_keys"]:
        print(f"  {label_a} ainult: {key_value}")

    print(
        f"- {label_b} poolel ilma {label_a} vasteta: "
        f"{len(comparison['right_only_keys'])}"
    )
    for key_value in comparison["right_only_keys"]:
        print(f"  {label_b} ainult: {key_value}")


def main():
    conn = get_connection()
    try:
        print_check_keys(
            conn=conn,
            source_a="staging.api_users",
            source_b="staging.user_status",
            key="email",
            label_a="API",
            label_b="CSV",
        )

        if relation_exists(conn, "staging.notification_preferences"):
            print_check_keys(
                conn=conn,
                source_a="staging.api_users",
                source_b="staging.notification_preferences",
                key="email",
                label_a="API",
                label_b="JSON",
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
