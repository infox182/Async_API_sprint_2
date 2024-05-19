import psycopg2
import os
import backoff

from psycopg2.extensions import connection as _connection
from contextlib import contextmanager

from etl.validation import FilmWork, Genre, Person_Vld
from data.query import MOVIES_QUERY, GENRES_QUERY, PERSONS_QUERY
from settings import settings


MAX_TRIES = settings.max_tries
MAX_TIME = settings.max_time


class PostgresExtractor:

    def __init__(self, dsl: dict, batch_size: int) -> None:
        self.batch_size = batch_size
        self.dsl = dsl

    @contextmanager
    def conn_context_pg(self, dsl: str) -> _connection:
        """Конекстный менеджер для подключения."""

        @backoff.on_exception(
            backoff.expo,
            psycopg2.OperationalError,
            max_tries=MAX_TRIES,
            max_time=MAX_TIME,
        )
        def get_connection(dsl: dict) -> _connection:
            """Получает подключение к Postgres."""
            return psycopg2.connect(**dsl)

        conn = get_connection(dsl)
        try:
            yield conn
        finally:
            conn.close()

    @backoff.on_exception(
        backoff.expo, psycopg2.OperationalError, max_tries=MAX_TRIES, max_time=MAX_TIME
    )
    def extract_data(self, state_datetime: str) -> dict:
        """Извлекает данные из Postgres."""
        with self.conn_context_pg(self.dsl) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                queries = {
                    "movies": (MOVIES_QUERY.format(date=state_datetime), FilmWork),
                    "genres": (GENRES_QUERY.format(date=state_datetime), Genre),
                    "persons": (PERSONS_QUERY.format(date=state_datetime), Person_Vld),
                }

                loaded_data = {key: [] for key in queries.keys()}

                for key, (query, ValidatorClass) in queries.items():
                    cursor.execute(query)
                    while True:
                        data = cursor.fetchmany(self.batch_size)
                        if data:
                            for one_batch in data:
                                loaded_data[key].append(
                                    ValidatorClass(**dict(one_batch)).model_dump(
                                        mode="json"
                                    )
                                )
                        else:
                            break
        return loaded_data
