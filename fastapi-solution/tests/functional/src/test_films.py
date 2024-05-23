import uuid
import pytest

from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star"}, {"status": 200, "length": 50}),
        ({"query": "Mashed potato"}, {"status": 200, "length": 0}),
        ({"query": "I am the Only One"}, {"status": 200, "length": 1}),
    ],
)
@pytest.mark.asyncio
async def test_search(
    generate_films,
    es_write_data,
    make_get_request,
    es_clearing,
    query_data,
    expected_answer,
):

    movie_index_name = test_settings.es_index_movie

    # 1. Генерируем данные для ES
    es_data = generate_films(60)

    single_movie = {
        "id": str(uuid.uuid4()),
        "imdb_rating": 8.5,
        "title": "I am the Only One",
    }
    es_data.append(single_movie)

    # 2. Загружаем данные в ES
    await es_write_data(movie_index_name, es_data)

    # 3. Запрашиваем данные из ES по API
    body, headers, status = await make_get_request("films/search", query_data)

    # 4. Проверяем ответ
    try:
        assert status == expected_answer["status"]
        assert len(body) == expected_answer["length"]
        if query_data["query"] == "I am the Only One":
            single_movie["uuid"] = single_movie.pop("id")
            assert body[0] == single_movie

    # 5. Удаляем индекс
    finally:
        await es_clearing(movie_index_name)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"page_size": 100}, {"status": 200, "length": 77}),
    ],
)
@pytest.mark.asyncio
async def test_all_films(
    generate_films,
    es_write_data,
    make_get_request,
    es_clearing,
    query_data,
    expected_answer,
):

    movie_index_name = test_settings.es_index_movie

    es_data = generate_films(77)

    await es_write_data(movie_index_name, es_data)

    body, headers, status = await make_get_request("films/", query_data)

    try:
        assert status == expected_answer["status"]
        assert len(body) == expected_answer["length"]

    finally:
        await es_clearing(movie_index_name)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({}, {"status": 200}),
    ],
)
@pytest.mark.asyncio
async def test_single_film(
    generate_films,
    make_normal_names,
    es_write_data,
    get_from_redis,
    make_get_request,
    es_clearing,
    redis_clearing,
    query_data,
    expected_answer,
):

    movie_index_name = test_settings.es_index_movie

    es_data = generate_films(1)
    single_movie = es_data[0]
    uuid_movie = single_movie["id"]

    try:
        # 1. Загружаем данные в ES
        await es_write_data(movie_index_name, es_data)

        # 2. Проверяем пустой ли redis
        redis_value = await get_from_redis(f"{movie_index_name}:{uuid_movie}")
        assert redis_value is None

        # 3. Запрашиваем данные из ES по API
        body, headers, status = await make_get_request(
            f"films/{uuid_movie}", query_data
        )

        # 4. Проверяем cтатус
        assert status == expected_answer["status"]

        # 5. Изменяем названия полей для проверки
        single_movie = make_normal_names(single_movie)
        # 6. Запрашиваем данные из redis
        redis_value = await get_from_redis(f"{movie_index_name}:{uuid_movie}")
        # 7. Проверяем ответ из ES
        assert body == single_movie
        # 7. Проверяем ответ из redis
        assert redis_value == single_movie

    finally:
        await es_clearing(movie_index_name)
        await redis_clearing()
