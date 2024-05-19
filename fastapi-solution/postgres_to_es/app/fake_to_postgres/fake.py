import json
import random

from faker import Faker

from fake_to_postgres.settings import (
    limit_movies,
    limit_genres,
    limit_persones,
    file_path,
    upload_limit,
)


type_movie_list = ["movie", "tv_show"]
roles_list = ["actor", "writer", "director"]


class JsonFileStorage:
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, "w", encoding="utf-8") as json_file:
            json.dump(state, json_file, ensure_ascii=False, indent=4)

    def retrieve_state(self) -> dict:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path) as json_file:
                data = json.load(json_file)
            return data
        except Exception:
            return {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: JsonFileStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value) -> None:
        """Установить состояние для определённого ключа."""
        data = self.storage.retrieve_state()
        data[key] = value
        self.storage.save_state(data)

    def get_state(self, key: str):
        """Получить состояние по определённому ключу."""
        data = self.storage.retrieve_state()
        return data.get(key)


jfs = JsonFileStorage(file_path)
st = State(jfs)


def create_fake_movies(fake: Faker, name: str) -> list[dict]:
    result = []
    uuid_list = []
    for _ in range(limit_movies):
        uuid = fake.uuid4()
        movie = dict(
            id=uuid,
            title=fake.text(max_nb_chars=50),
            description=fake.text(max_nb_chars=200),
            creation_date=fake.date_time(),
            file_path=None,
            rating=round(fake.pyfloat(min_value=0, max_value=100), 2),
            type=random.choice(type_movie_list),
        )
        uuid_list.append(uuid)
        result.append(movie)
    st.set_state(name, uuid_list)
    return result


def create_fake_persones(fake: Faker, name: str) -> list[dict]:
    result = []
    uuid_list = []
    for _ in range(limit_persones):
        uuid = fake.uuid4()
        person = dict(id=uuid, full_name=fake.name())
        uuid_list.append(uuid)
        result.append(person)
    st.set_state(name, uuid_list)
    return result


def create_fake_genres(fake: Faker, name: str) -> list[dict]:
    result = []
    uuid_list = []
    for word in fake.words(nb=limit_genres, part_of_speech="noun", unique=True):
        uuid = fake.uuid4()
        genre = dict(id=uuid, name=word, description=fake.text(max_nb_chars=150))
        uuid_list.append(uuid)
        result.append(genre)
    st.set_state(name, uuid_list)
    return result


def create_genre_film_work(fake: Faker, name: str) -> list[dict]:
    genres_uuid = st.get_state("genre")
    movies_uuid = st.get_state("film_work")
    result = []
    for movie in movies_uuid:
        gr_uuids = random.sample(genres_uuid, random.randint(2, 3))
        for gr_uuid in gr_uuids:
            genre_film_work = dict(
                id=fake.uuid4(), film_work_id=movie, genre_id=gr_uuid
            )
            result.append(genre_film_work)
    return result


def create_person_film_work(fake: Faker, name: str) -> list[dict]:
    persones_uuid = st.get_state("person")
    movies_uuid = st.get_state("film_work")
    result = []
    for movie in movies_uuid:
        pr_uuids = random.sample(persones_uuid, random.randint(4, 5))
        for pr_uuid in pr_uuids:
            genre_film_work = dict(
                id=fake.uuid4(),
                film_work_id=movie,
                person_id=pr_uuid,
                role=random.choice(roles_list),
            )
            result.append(genre_film_work)
    return result


table_names_func = {
    "film_work": create_fake_movies,
    "genre": create_fake_genres,
    "person": create_fake_persones,
    "genre_film_work": create_genre_film_work,
    "person_film_work": create_person_film_work,
}


def create_fake_table(table_name):
    fake = Faker()
    data = table_names_func[table_name](fake, table_name)
    len_data = len(data)
    end = False
    iter_count = 0
    while not end:
        start_i = iter_count * upload_limit
        end_i = start_i + upload_limit
        result = data[start_i:end_i]
        if end_i >= len_data:
            result = data[start_i:]
            end = True
        yield result
        iter_count += 1
