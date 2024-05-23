import asyncio
import json
import pytest
import pytest_asyncio
import os

from aiohttp import ClientSession, RequestInfo
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from tests.functional.settings import test_settings


async def list_in_parts(data: list):
    len_data = len(data)
    end = False
    limit = test_settings.download_limit
    iter_count = 0
    while not end:
        start_i = iter_count * limit
        end_i = start_i + limit
        result = data[start_i:end_i]
        if end_i >= len_data:
            result = data[start_i:]
            end = True
        yield result
        iter_count += 1


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{test_settings.es_host}:{test_settings.es_port}'
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session')
async def http_session():
    sess = ClientSession()
    yield sess
    await sess.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    sess = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield sess
    await sess.close()


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(index: str, data: list[dict]):
        if not await es_client.indices.exists(index=index):
            await es_client.indices.create(
                index=index,
                body=test_settings.es_index_mapping[index])
        async for part in list_in_parts(data):
            bulk_data = []
            for elem in part:
                elem_id = elem['id']
                bulk_data.append({
                        '_index': index,
                        '_id': elem_id,
                        '_source': elem
                    }
                )
            await async_bulk(es_client, bulk_data)
    return inner


@pytest_asyncio.fixture
def es_clearing(es_client: AsyncElasticsearch):
    async def inner(index: str):
        await es_client.indices.delete(index, ignore_unavailable=True)
    return inner


@pytest_asyncio.fixture
def make_get_request(http_session: ClientSession):
    async def inner(path: str, params: dict = {}) -> RequestInfo:
        api_path = 'api/v1/'
        url = os.path.join(test_settings.service_url, api_path, path)
        async with http_session.get(url, params=params) as response:
            body = await response.json(content_type=None)
            headers = response.headers
            status = response.status
        return body, headers, status
    return inner


@pytest_asyncio.fixture
def get_from_redis(redis_client: Redis):
    async def inner(key: str) -> dict:
        data = await redis_client.get(key)
        if data is None:
            return None
        return json.loads(data)
    return inner


@pytest_asyncio.fixture
def redis_clearing(redis_client: Redis):
    async def inner() -> None:
        await redis_client.flushdb(asynchronous=True)
    return inner
