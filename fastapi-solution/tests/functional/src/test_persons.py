import uuid
import pytest

from http import HTTPStatus

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_person_search(es_write_data, es_clearing, make_get_request):
    index = test_settings.es_index_person
    test_uuid = str(uuid.uuid4())
    person_es_data = [{"id": test_uuid, "full_name": "Alex Gate"}]
    uuid_film_list = (str(uuid.uuid4()), str(uuid.uuid4()))
    film_es_data = [
        {
            "id": i,
            "imdb_rating": 8.5,
            "creation_date": "2020-01-01",
            "genres": [{"id": str(uuid.uuid4()), "name": "Action"}],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "actors": [
                {"id": test_uuid, "name": "Alex Gate"},
            ],
            "writers": [
                {"id": test_uuid, "name": "Alex Gate"},
            ],
            "directors": [
                {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
            ],
        }
        for i in uuid_film_list
    ]

    await es_write_data(test_settings.es_index_movie, film_es_data)
    await es_write_data(index, person_es_data)
    body, headers, status = await make_get_request("persons/search", {"query": "alex"})
    expected_body = [
        {
            "uuid": test_uuid,
            "full_name": "Alex Gate",
            "films": [
                {"uuid": i, "roles": ["actor", "writer"]} for i in uuid_film_list
            ],
        }
    ]
    try:
        assert status == HTTPStatus.OK
        assert body == expected_body
    finally:
        await es_clearing(index)
        await es_clearing(test_settings.es_index_movie)


@pytest.mark.asyncio
async def test_person_get_by_id(
    es_write_data,
    es_clearing,
    make_get_request,
    get_from_redis,
    redis_clearing,
    generate_films,
):
    index = test_settings.es_index_person
    test_uuid = str(uuid.uuid4())
    data = [{"id": test_uuid, "full_name": "Alex Gate"}]

    await es_write_data(test_settings.es_index_movie, generate_films(1))
    await es_write_data(index, data)
    redis_value = await get_from_redis(f"{index}:{test_uuid}")
    assert redis_value is None
    body, headers, status = await make_get_request("persons/" + test_uuid)
    expected_body = {"uuid": test_uuid, "full_name": "Alex Gate", "films": []}
    redis_value = await get_from_redis(f"{index}:{test_uuid}")
    assert status == HTTPStatus.OK
    assert body == expected_body
    assert redis_value == expected_body
    await es_clearing(index)
    await es_clearing(test_settings.es_index_movie)
    await redis_clearing()


@pytest.mark.asyncio
async def test_person_films(es_write_data, es_clearing, make_get_request):
    index = test_settings.es_index_person
    test_uuid = str(uuid.uuid4())
    person_es_data = [{"id": test_uuid, "full_name": "Alex Gate"}]
    uuid_film_list = (str(uuid.uuid4()), str(uuid.uuid4()))
    film_es_data = [
        {
            "id": i,
            "imdb_rating": 8.5,
            "creation_date": "2020-01-01",
            "genres": [{"id": str(uuid.uuid4()), "name": "Action"}],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "actors": [
                {"id": test_uuid, "name": "Alex Gate"},
            ],
            "writers": [
                {"id": test_uuid, "name": "Alex Gate"},
            ],
            "directors": [
                {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
            ],
        }
        for i in uuid_film_list
    ]

    await es_write_data(test_settings.es_index_movie, film_es_data)
    await es_write_data(index, person_es_data)
    body, headers, status = await make_get_request("persons/" + test_uuid + "/film")
    expected_body = [
        {"uuid": i, "title": "The Star", "imdb_rating": 8.5} for i in uuid_film_list
    ]
    try:
        assert status == HTTPStatus.OK
        assert body == expected_body
    finally:
        await es_clearing(index)
        await es_clearing(test_settings.es_index_movie)
