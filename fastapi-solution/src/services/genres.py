from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genres import Genre
from services.base import BaseGetById, BaseGetAll


class GenreService(BaseGetById, BaseGetAll):
    cache_expire_in_seconds = 60 * 5
    index_name = "genres"
    model_get_by_id = Genre
    model_es_get_by_id = Genre
    model_get_all = Genre

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
