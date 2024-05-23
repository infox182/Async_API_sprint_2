import sys
import datetime
import uuid
import aiohttp
import pytest
import time
import asyncio

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_search(es_write_data, make_get_request):

    # 1. Генерируем данные для ES
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
        for _ in range(60)
    ]

    movie_index_name = test_settings.es_index_movie

    # 2. Загружаем данные в ES
    await es_write_data(movie_index_name, es_data)

    # 3. Запрашиваем данные из ES по API
    query_data = {"query": "The Star"}
    body, headers, status = await make_get_request("films/search", query_data)

    # 4. Проверяем ответ
    assert status == 200
    assert len(body) == 50
