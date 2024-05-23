import os
import time
import datetime
import pathlib
import sys

from loguru import logger

from sqlite_to_postgres.transfer import make_transfer

# from fake_to_postgres.main import main as make_transfer
from state.state import State, JsonFileStorage
from etl.loader import ElasticsearchLoader
from etl.extractor import PostgresExtractor
from settings import settings


BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_PATH = os.path.join(BASE_DIR, settings.log_path)

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)
logger.add(LOG_PATH, retention="30 days")


@logger.catch()
def start_pipilene() -> None:
    """ "Запускает процесс ETL."""

    transfer_status = make_transfer(dict(settings.pg))
    logger.info(transfer_status)
    # time.sleep(20)
    # make_transfer()

    storage = JsonFileStorage(settings.json_path)
    state = State(storage)
    extractor = PostgresExtractor(dict(settings.pg), 100)
    loader = ElasticsearchLoader(dict(settings.es), settings.index_name)

    while True:
        logger.info("Начало обновления")
        update_count = 0
        state_datetime = state.get_state("last_modified")
        if state_datetime:
            start_datetime = state_datetime
        else:
            start_datetime = datetime.date.min.isoformat()

        for key, value in extractor.extract_data(start_datetime).items():
            update_count += len(value)
            loader.load_data(key, value)
        loader.close_connection()

        state.set_state("last_modified", datetime.datetime.now().isoformat())
        logger.info(f"Конец. Всего обновлено {update_count} записей")
        time.sleep(settings.sleep_time)


if __name__ == "__main__":
    start_pipilene()
