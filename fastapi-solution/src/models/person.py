from enum import Enum
from pydantic import Field

from models.base import MyBaseModel


class RoleEnum(str, Enum):
    actor = "actor"
    writer = "writer"
    director = "director"


class FilmForPerson(MyBaseModel):
    roles: list[RoleEnum]


class Person(MyBaseModel):
    full_name: str = Field(alias="name")


class PersonWithFilms(MyBaseModel):
    full_name: str = Field()
    films: list[FilmForPerson]
