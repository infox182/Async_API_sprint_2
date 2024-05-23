from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from pydantic import BaseModel


class AbstractGetById(ABC):
    @abstractmethod
    async def index_name(self, index: str):
        pass

    @abstractmethod
    async def model_get_by_id(self, model: BaseModel):
        pass

    @abstractmethod
    async def model_es_get_by_id(self, model: BaseModel):
        pass

    @abstractmethod
    async def get_by_id(self, obj_id: str):
        pass

    @abstractmethod
    async def _get_obj_from_elastic(self, obj_id: str):
        pass

    @abstractmethod
    async def _get_obj_from_cache(self, obj_id: str):
        pass

    @abstractmethod
    async def _put_obj_to_cache(self, obj: dict):
        pass


class BaseGetById(AbstractGetById):
    cache_expire_in_seconds = 60 * 5
    index_name = "example"
    model_get_by_id = BaseModel
    model_es_get_by_id = BaseModel

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, obj_id: str) -> BaseModel:
        obj = await self._get_obj_from_cache(obj_id)
        if not obj:
            obj = await self._get_obj_from_elastic(obj_id)
            if not obj:
                return None
            await self._put_obj_to_cache(obj)
        return obj

    async def _get_obj_from_elastic(self, obj_id: str):
        try:
            doc = await self.elastic.get(index=self.index_name, id=obj_id)
        except NotFoundError:
            return None
        return self.model_es_get_by_id(**doc["_source"])

    async def _get_obj_from_cache(self, obj_id: str) -> BaseModel | None:
        key = self.index_name + ":" + obj_id
        data = await self.redis.get(key)
        if not data:
            return None

        return self.model_get_by_id.model_validate_json(data)

    async def _put_obj_to_cache(self, obj: BaseModel):
        key = self.index_name + ":" + obj.uuid
        await self.redis.set(key, obj.model_dump_json(), self.cache_expire_in_seconds)


class AbstractSearch(ABC):
    @abstractmethod
    async def index_name(self, index: str):
        pass

    @abstractmethod
    async def model_search(self, model: BaseModel):
        pass

    @abstractmethod
    async def search_field(self, field: str):
        pass

    @abstractmethod
    async def search(self, query: str, page_size: int = 50, page_number: int = 1):
        pass


class BaseSearch(AbstractSearch):
    index_name = "example"
    model_search = BaseModel
    search_field = "example"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search(
        self, query: str, page_size: int = 50, page_number: int = 1
    ) -> list[BaseModel]:
        query = {
            "query": {"match": {self.search_field: query}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }
        response = await self.elastic.search(index=self.index_name, body=query)
        data = response["hits"]["hits"]
        return [self.model_search(**i["_source"]) for i in data]


class AbstractGetAll(ABC):
    @abstractmethod
    async def index_name(self, index: str):
        pass

    @abstractmethod
    async def model_get_all(self, model: BaseModel):
        pass

    @abstractmethod
    async def get_all(self, page_size: int = 50, page_number: int = 1):
        pass


class BaseGetAll(AbstractGetAll):
    index_name = "example"
    model_get_all = BaseModel

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_all(
        self, page_size: int = 50, page_number: int = 1
    ) -> list[BaseModel]:
        query = {"size": page_size, "from": (page_number - 1) * page_size}
        response = await self.elastic.search(index=self.index_name, body=query)
        data = response["hits"]["hits"]
        return [self.model_get_all(**i["_source"]) for i in data]
