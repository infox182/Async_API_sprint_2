import sys
import pathlib
import time
import backoff

from elasticsearch import Elasticsearch

sys.path.append("/tests/functional")

from settings import test_settings


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=test_settings.max_tries,
    max_time=test_settings.max_time,
)
def es_ping(es_client):
    if es_client.ping():
        print("ES Работает")
        return None
    raise Exception


if __name__ == "__main__":
    es_client = Elasticsearch(
        hosts=[f"{test_settings.es_host}:{test_settings.es_port}"],
        validate_cert=False,
        use_ssl=False,
    )
    es_ping(es_client)
