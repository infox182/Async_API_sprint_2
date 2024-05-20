from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmBase

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index_name = "movies"

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index=self.index_name, id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        key = self.index_name + ':' + film_id
        data = await self.redis.get(key)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        key = self.index_name + ':' + film.uuid
        await self.redis.set(key, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def search(
        self, query: str, page_size: int = 50, page_number: int = 1
    ) -> list[FilmBase]:
        query = {
            "query": {"match": {"title": query}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }
        response = await self.elastic.search(index=self.index_name, body=query)
        data = response["hits"]["hits"]
        return [FilmBase(**i["_source"]) for i in data]

    async def get_all(
        self,
        genre: str | None = None,
        sort: str = "-imdb_rating",
        page_size: int = 50,
        page_number: int = 1,
    ) -> list[FilmBase]:
        if "+" in sort:
            sort = sort[1:]
            sort_type = "asc"
        elif "-" in sort:
            sort = sort[1:]
            sort_type = "desc"
        else:
            sort_type = "desc"
        if genre is None:
            query = {
                "size": page_size,
                "from": (page_number - 1) * page_size,
                "sort": [{sort: sort_type}],
            }
        else:
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "genres",
                                    "query": {"match": {"genres.id": genre}},
                                }
                            },
                        ]
                    }
                },
                "size": page_size,
                "from": (page_number - 1) * page_size,
                "sort": [{sort: sort_type}],
            }
        response = await self.elastic.search(index=self.index_name, body=query)
        data = response["hits"]["hits"]
        return [FilmBase(**i["_source"]) for i in data]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
