import sqlite3

from sqlite3 import Connection
from contextlib import contextmanager
from collections import defaultdict

from sqlite_to_postgres.model_data import (
    FilmWork,
    Genre,
    Person,
    GenreFilmWork,
    PersonFilmWork,
    DATACLASS_MATCH,
    FIELDS_MATCH,
)


@contextmanager
def conn_context(db_path: str) -> Connection:
    """Получает подключение к SQLLite."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def extract_data(db_path: str, n: int = 100) -> dict:
    """Извлекает данные из БД SQLLite."""
    with conn_context(db_path) as conn:
        for table, data_wrapper in list(DATACLASS_MATCH.items()):
            curs = conn.cursor()
            curs.execute(f"SELECT * FROM {table};")
            while True:
                data = curs.fetchmany(n)
                if data:
                    loaded_data = defaultdict(list)
                    for batch in data:
                        loaded_data[table].append(data_wrapper(**batch))
                    yield loaded_data
                else:
                    break
