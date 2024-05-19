import pathlib
import os
import backoff

from sqlite_to_postgres.lite_db import extract_data
from sqlite_to_postgres.postgre_db import save_all_data, get_conn_pg
from state.state import State, JsonFileStorage

BASE_DIR = pathlib.Path(__file__).parent.resolve()


def make_transfer(dsl: dict) -> str:
    """Основной метод загрузки данных из SQLite в Postgres."""

    key_transfer = "sqllite_transfer"
    db_path = os.path.join(BASE_DIR, "files/db.sqlite")
    storage_path = os.path.join(BASE_DIR, "files/storage.json")
    storage = JsonFileStorage(storage_path)
    state = State(storage)
    transfer_status = state.get_state(key_transfer)
    if transfer_status:
        return "Трансфер уже был"

    connection = get_conn_pg(dsl)
    for data in extract_data(db_path):
        save_all_data(connection, data)
    connection.close()

    state.set_state(key_transfer, "good")
    return "Трансфер прошел успешно"
