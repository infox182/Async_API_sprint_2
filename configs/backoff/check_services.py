import logging
import os
import time

import backoff
import requests
import psycopg2
from redis import Redis
from psycopg2 import OperationalError as PostgresOperationalError
from requests.exceptions import ConnectionError as RequestsConnectionError
from redis.exceptions import ConnectionError as RedisConnectionError

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
POSTGRES_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432),  # Установим 5432 по умолчанию
}

ELASTICSEARCH_URL = "http://elasticsearch:9200"
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
}


@backoff.on_exception(backoff.expo, PostgresOperationalError, max_tries=10, logger=logger)
def check_postgres():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.close()
    except PostgresOperationalError as e:
        logger.error("PostgreSQL is not available yet")
        raise


@backoff.on_exception(backoff.expo, RequestsConnectionError, max_tries=10, logger=logger)
def check_elasticsearch():
    try:
        response = requests.get(ELASTICSEARCH_URL)
        if response.status_code != 200:
            raise RequestsConnectionError("Elasticsearch is not available yet")
    except RequestsConnectionError as e:
        logger.error("Elasticsearch is not available yet")
        raise


@backoff.on_exception(backoff.expo, RedisConnectionError, max_tries=10, logger=logger)
def check_redis():
    try:
        client = Redis(**REDIS_CONFIG)
        client.ping()
    except RedisConnectionError as e:
        logger.error("Redis is not available yet")
        raise


def main():
    try:
        logger.info("Checking PostgreSQL...")
        check_postgres()
        logger.info("PostgreSQL is available")

        logger.info("Checking Elasticsearch...")
        check_elasticsearch()
        logger.info("Elasticsearch is available")

        logger.info("Checking Redis...")
        check_redis()
        logger.info("Redis is available")

        logger.info("All services are available")
    except Exception as e:
        logger.error(f"Service check failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
