import sys
import pathlib
import time
import backoff

from redis import Redis

sys.path.append("/tests/functional")

from settings import test_settings


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=test_settings.max_tries,
    max_time=test_settings.max_time,
)
def redis_ping(redis_client):
    if redis_client.ping():
        print("Redis Работает")
        return None
    raise Exception


if __name__ == "__main__":
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    redis_ping(redis_client)
