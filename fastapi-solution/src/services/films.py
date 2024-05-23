from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.films import Film, FilmBase
from services.base import BaseGetById, BaseSearch, BaseGetAll


class FilmService(BaseGetById, BaseSearch, BaseGetAll):
    cache_expire_in_seconds = 60 * 5
    index_name = "movies"
    model_get_by_id = Film
    model_es_get_by_id = Film
    model_search = FilmBase
    search_field = "title"
    model_get_all = FilmBase

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

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
