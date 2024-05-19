from datetime import datetime

from models.base import MyBaseModel
from models.genre import GenreForFilm
from models.person import Person


class Film(MyBaseModel):
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    creation_date: str | None = None
    genres: list[GenreForFilm] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []


class FilmByPerson(MyBaseModel):
    title: str
    imdb_rating: float = None


class FilmBase(MyBaseModel):
    title: str
    imdb_rating: float = None
