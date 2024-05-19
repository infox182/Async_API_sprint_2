import psycopg2
import time
import backoff
import os


from sqlite_to_postgres.model_data import check_column
from psycopg2.extras import execute_batch
from psycopg2.extensions import connection as _connection
from contextlib import contextmanager
from dataclasses import astuple, fields
from settings import settings


MAX_TRIES = settings.max_tries
MAX_TIME = settings.max_time


@backoff.on_exception(
    backoff.expo, psycopg2.OperationalError, max_tries=MAX_TRIES, max_time=MAX_TIME
)
def get_conn_pg(dsl: dict) -> _connection:
    """Получает подключение к Postgres."""
    conn = psycopg2.connect(**dsl)
    return conn


def save_all_data(conn: _connection, data: dict) -> None:
    """Сохраняет все поступившие данные в Postgres."""
    for table, table_data in list(data.items()):
        table_data = data[table]
        temp_row = table_data[0]

        values = [astuple(row) for row in table_data]
        column_names = [check_column(field.name) for field in fields(temp_row)]
        column_names_str = ",".join(column_names)
        col_count = ", ".join(["%s"] * len(column_names))

        query = (
            f"INSERT INTO content.{table} ({column_names_str}) VALUES ({col_count})"
            f"ON CONFLICT (id) DO NOTHING;"
        )

        curs = conn.cursor()
        execute_batch(curs, query, values)
        conn.commit()
