import uuid
import pytest

from http import HTTPStatus

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_genre_get_by_id(es_write_data, es_clearing, make_get_request):
    index = test_settings.es_index_genre
    test_uuid = str(uuid.uuid4())
    genre_es_data = [
        {"id": test_uuid, "name": "Action", "description": "Action movies"}
    ]

    await es_write_data(index, genre_es_data)
    body, headers, status = await make_get_request("genres/" + test_uuid)
    expected_body = {
        "uuid": test_uuid,
        "name": "Action",
        "description": "Action movies",
    }
    try:
        assert status == HTTPStatus.OK
        assert body == expected_body
    finally:
        await es_clearing(index)


@pytest.mark.asyncio
async def test_genre_get_all(es_write_data, es_clearing, make_get_request):
    index = test_settings.es_index_genre
    test_uuid1 = str(uuid.uuid4())
    test_uuid2 = str(uuid.uuid4())
    genre_es_data = [
        {"id": test_uuid1, "name": "Action", "description": "Action movies"},
        {"id": test_uuid2, "name": "Drama", "description": "Drama movies"},
    ]

    await es_write_data(index, genre_es_data)
    body, headers, status = await make_get_request("genres")
    expected_body = [
        {"uuid": test_uuid1, "name": "Action", "description": "Action movies"},
        {"uuid": test_uuid2, "name": "Drama", "description": "Drama movies"},
    ]
    try:
        assert status == HTTPStatus.OK
        assert body == expected_body
    finally:
        await es_clearing(index)
