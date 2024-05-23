import uuid

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TypeFilmworkEnum(str, Enum):
    movie = "movie"
    tv_show = "tv_show"


@dataclass()
class Filmwork:
    title: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    creation_date: datetime = field(default=None)
    type: TypeFilmworkEnum = field(default=None)
    rating: float = field(default=0.0)
    file_path: str = field(default=None)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class Genre:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = field(default=None)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass()
class Person:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass()
class GenreFilmwork:
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default_factory=datetime.now)


@dataclass()
class PersonFilmwork:
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default_factory=datetime.now)
