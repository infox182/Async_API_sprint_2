import os

from dotenv import load_dotenv
from fake_to_postgres.sсhemes import (
    Filmwork,
    Genre,
    Person,
    GenreFilmwork,
    PersonFilmwork,
)

load_dotenv()

test = os.environ.get("DEBUG", False) == "True"

upload_limit = 100

limit_movies = 200000
limit_genres = 200
limit_persones = 1000

file_path = "uuid_list.json"

dsn = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", 5432),
    "options": "-c search_path=content",
}

db_path = "sqlite_to_postgres/db.sqlite"

table_names = ["film_work", "genre", "person", "genre_film_work", "person_film_work"]

table_schemes_dict = {
    "film_work": Filmwork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmwork,
    "person_film_work": PersonFilmwork,
}

conflict_fields = {
    "film_work": "id",
    "genre": "id",
    "person": "id",
    "genre_film_work": "genre_id, film_work_id",
    "person_film_work": "person_id, film_work_id, role",
}


unique_pair = {
    "film_work": None,
    "genre": None,
    "person": None,
    "genre_film_work": ("genre_id", "film_work_id"),
    "person_film_work": ("person_id", "film_work_id", "role"),
}
