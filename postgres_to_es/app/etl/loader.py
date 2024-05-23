import os
import elastic_transport
import backoff

from elasticsearch import Elasticsearch, helpers

from data.es_schema import SCHEMAS
from settings import settings


MAX_TRIES = settings.max_tries
MAX_TIME = settings.max_time


class ElasticsearchLoader:

    def __init__(self, dsl: dict, index_name: str) -> None:
        self.index_name = index_name
        self.dsl = dsl
        self.es_client = None
        self.get_client()
        self.make_index()

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionTimeout, elastic_transport.ConnectionError),
        max_tries=MAX_TRIES,
        max_time=MAX_TIME,
    )
    def get_client(self) -> None:
        """Получает клиент для работы c ES и подключения к ES."""
        self.es_client = Elasticsearch(hosts=[self.dsl])

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionTimeout, elastic_transport.ConnectionError),
        max_tries=MAX_TRIES,
        max_time=MAX_TIME,
    )
    def make_index(self) -> None:
        """Создает индекс в ES."""
        for ind_name, schema in zip(self.index_name, SCHEMAS):
            if not self.es_client.indices.exists(index=ind_name):
                self.es_client.indices.create(index=ind_name, body=schema)

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionTimeout, elastic_transport.ConnectionError),
        max_tries=MAX_TRIES,
        max_time=MAX_TIME,
    )
    def make_load(self, key: str, body_dt: list) -> tuple:
        """Загружает данные в ES."""
        actions = [
            {"_index": key, "_id": one_batch["id"], "_source": one_batch}
            for one_batch in body_dt
        ]
        res = helpers.bulk(self.es_client, actions)
        return res

    def close_connection(self) -> None:
        """Закрывает соединение с ES."""
        if self.es_client:
            self.es_client.close()
        self.es_client = None

    def load_data(self, key: str, body_dt: list) -> tuple:
        """Загружает данные в ES с восстановлением соединения."""
        if not self.es_client:
            self.get_client()
        return self.make_load(key, body_dt)
