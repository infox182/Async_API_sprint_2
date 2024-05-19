from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import PersonWithFilms, Person, FilmForPerson
from models.film import FilmByPerson

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index_name = "persons"

    async def get_by_id(self, obj_id: str) -> Optional[PersonWithFilms]:
        obj = await self._get_person_with_films(obj_id)
        return obj

    async def search(
        self, query: str, page_size: int = 50, page_number: int = 1
    ) -> list:
        objs = await self._get_objects_from_search(query, page_size, page_number)
        return objs

    async def get_films(
        self, obj_id: str, page_size: int = 50, page_number: int = 1
    ) -> list:
        objs = await self._get_films_by_person(obj_id, page_size, page_number)
        return [FilmByPerson(**i["_source"]) for i in objs]

    async def _get_films_by_person(
        self, obj_id: str, page_size: int = 50, page_number: int = 1
    ) -> list:
        query = await self._create_film_by_person_query(obj_id, page_size, page_number)
        response = await self.elastic.search(index="movies", body=query)
        return response["hits"]["hits"]

    async def _get_objects_from_search(
        self, query: str, page_size: int = 50, page_number: int = 1
    ) -> list[PersonWithFilms]:
        query = {
            "query": {"match": {"full_name": query}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }
        response = await self.elastic.search(index=self.index_name, body=query)
        data = response["hits"]["hits"]
        result = []
        for person in data:
            person_id = person["_id"]
            person_dict = person["_source"]
            person_dict["films"] = await self._get_films_by_person_with_role(person_id)
            result.append(PersonWithFilms(**person_dict))
        return result

    async def _get_person_with_films(self, person_id: str) -> PersonWithFilms:
        obj = await self._get_from_cache(person_id)
        if not obj:
            obj = await self._get_from_elastic(person_id)
            if not obj:
                return None
            await self._put_to_cache(obj)
        person_dict = obj.dict()
        person_dict["films"] = await self._get_films_by_person_with_role(
            person_dict["uuid"]
        )
        return PersonWithFilms(**person_dict)

    async def _get_films_by_person_with_role(
        self, person_id: str
    ) -> list[FilmForPerson]:
        films = await self._get_films_by_person(person_id)
        result = []
        for film in films:
            roles = []
            film_source = film["_source"]
            actors_id = [i["id"] for i in film_source["actors"]]
            writers_id = [i["id"] for i in film_source["writers"]]
            directors_id = [i["id"] for i in film_source["directors"]]
            if person_id in actors_id:
                roles.append("actor")
            if person_id in writers_id:
                roles.append("writer")
            if person_id in directors_id:
                roles.append("director")
            result.append(FilmForPerson(id=film_source["id"], roles=roles))
        return result

    async def _get_from_elastic(self, obj_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index=self.index_name, id=obj_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _get_from_cache(self, obj_id: str) -> Optional[Person]:
        data = await self.redis.get(obj_id)
        if not data:
            return None

        obj = Person.parse_raw(data)
        return obj

    async def _put_to_cache(self, obj: Person):
        await self.redis.set(obj.uuid, obj.json(), CACHE_EXPIRE_IN_SECONDS)

    async def _create_film_by_person_query(
        self, person_id: str, page_size: int = 50, page_number: int = 1
    ) -> dict:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"match": {"actors.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"match": {"writers.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"match": {"directors.id": person_id}},
                            }
                        },
                    ]
                }
            },
            "size": page_size,
            "from": (page_number - 1) * page_size,
            "sort": [{"imdb_rating": "desc"}],
        }
        return query


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
