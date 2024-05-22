import sys
import pathlib
import time

from redis import Redis

sys.path.append("/tests/functional")

from settings import test_settings

if __name__ == "__main__":
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    while True:
        if redis_client.ping():
            print("Redis Работает")
            break
        time.sleep(1)
