import psycopg2.extras

from dataclasses import astuple, fields


def write_to_postgres(
    data: list,
    table_name: str,
    scheme: object,
    conflict_fields: str,
    conn: psycopg2.extensions.connection,
    cursor: psycopg2.extensions.cursor,
):
    rows = []
    row_for_columns = scheme(**data[0])
    column_names = [field.name for field in fields(row_for_columns)]
    column_names_str = ",".join(column_names)
    for row in data:
        row_scheme = scheme(**row)
        rows.append(row_scheme)
    col_count = ", ".join(["%s"] * len(column_names))
    bind_values = ",".join(
        cursor.mogrify(f"({col_count})", astuple(row)).decode("utf-8") for row in rows
    )
    query = (
        f"INSERT INTO content.{table_name} "
        f"({column_names_str}) VALUES {bind_values}"
        f"ON CONFLICT ({conflict_fields}) DO NOTHING;"
    )
    cursor.execute(query)
