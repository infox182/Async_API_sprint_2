import asyncio
import json
import pytest
import pytest_asyncio
import os
import uuid

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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(
        hosts=f"{test_settings.es_host}:{test_settings.es_port}"
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def http_session():
    sess = ClientSession()
    yield sess
    await sess.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    sess = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield sess
    await sess.close()


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(index: str, data: list[dict]):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index, ignore_unavailable=True)
        await es_client.indices.create(
            index=index, body=test_settings.es_index_mapping[index]
        )
        async for part in list_in_parts(data):
            bulk_data = []
            for elem in part:
                elem_id = elem["id"]
                bulk_data.append({"_index": index, "_id": elem_id, "_source": elem})
            await async_bulk(es_client, bulk_data)
            await asyncio.sleep(1)

    return inner


@pytest_asyncio.fixture
def es_clearing(es_client: AsyncElasticsearch):
    async def inner(index: str):
        await es_client.indices.delete(index, ignore_unavailable=True)

    return inner


@pytest_asyncio.fixture
def make_get_request(http_session: ClientSession):
    async def inner(path: str, params: dict = {}) -> RequestInfo:
        api_path = "api/v1/"
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


@pytest.fixture
def generate_films():
    def inner(n: int) -> list[dict]:
        es_data = [
            {
                "id": str(uuid.uuid4()),
                "imdb_rating": 8.5,
                "creation_date": "2020-01-01",
                "genres": [{"id": str(uuid.uuid4()), "name": "Action"}],
                "title": "The Star",
                "description": "New World",
                "directors_names": ["Stan"],
                "actors_names": ["Ann", "Bob"],
                "writers_names": ["Ben", "Howard"],
                "actors": [
                    {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                    {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
                ],
                "writers": [
                    {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                    {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
                ],
                "directors": [
                    {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                    {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
                ],
            }
            for _ in range(n)
        ]
        return es_data

    return inner


@pytest.fixture
def make_normal_names():
    def inner(body: dict) -> dict:
        body["uuid"] = body.pop("id")
        for field in ["directors_names", "actors_names", "writers_names"]:
            if field in body:
                body.pop(field)
        for field in ["genres", "directors", "actors", "writers"]:
            if field in body:
                for i, v in enumerate(body[field]):
                    if "id" in v:
                        body[field][i]["uuid"] = body[field][i].pop("id")
                    if "name" in v and field != "genres":
                        body[field][i]["full_name"] = body[field][i].pop("name")
        return body

    return inner
