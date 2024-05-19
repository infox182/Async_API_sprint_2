import sqlite3

from contextlib import contextmanager
from fake_to_postgres.settings import upload_limit


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def read_sqlite_table(table_name: str, conn: sqlite3.Connection):
    """Чтение таблицы из sqlite по названию таблицы."""
    curs = conn.cursor()
    curs.execute(f"SELECT * FROM {table_name};")
    result = curs.fetchmany(upload_limit)
    while result:
        yield [dict(row) for row in result]
        result = curs.fetchmany(upload_limit)
