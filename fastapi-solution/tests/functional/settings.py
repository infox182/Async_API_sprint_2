import sys
import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

sys.path.append("/tests/functional")
BASE_DIR = pathlib.Path(__file__).parent.resolve()
if str(BASE_DIR) == "/tests/functional":
    from testdata.es_mapping import SCHEMAS
else:
    from tests.functional.testdata.es_mapping import SCHEMAS


class TestSettings(BaseSettings):
    es_host: str = Field("127.0.0.1", alias="ELASTIC_HOST")
    es_port: int = Field(9200, alias="ELASTIC_PORT")
    es_index_movie: str = "movies"
    es_index_person: str = "persons"
    es_index_genre: str = "genres"
    es_id_field: str = "uuid"
    es_index_mapping: dict = SCHEMAS

    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    service_url: str = Field("http://127.0.0.1:8000", alias="SERVICE_URL")

    download_limit: int = 200
    max_tries: int = 7
    max_time: int = 25


test_settings = TestSettings()
