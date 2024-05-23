
import datetime
import uuid

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_person_search():
    pass


@pytest.mark.asyncio
async def test_person_get_by_id(
    es_write_data, es_clearing, make_get_request,
    get_from_redis, redis_clearing, generate_films
):
    index = test_settings.es_index_person
    test_uuid = str(uuid.uuid4())
    data = [
        {
            'id': test_uuid,
            'full_name': 'Alex Gate'
        }
    ]
    
    await es_write_data(test_settings.es_index_movie, generate_films(1))
    await es_write_data(index, data)
    redis_value = await get_from_redis(f'{index}:{test_uuid}')
    assert redis_value is None
    body, headers, status = await make_get_request('persons/' + test_uuid)
    expected_body = {
        'uuid': test_uuid,
        'full_name': 'Alex Gate',
        'films': []
    }
    redis_value = await get_from_redis(f'{index}:{test_uuid}')
    assert status == 200
    assert body == expected_body
    assert redis_value == expected_body
    await es_clearing(index)
    await es_clearing(test_settings.es_index_movie)
    await redis_clearing()


@pytest.mark.asyncio
async def test_person_films(
    es_write_data, es_clearing, make_get_request,
    get_from_redis, redis_clearing
):
    pass
