import psycopg2.extras

from datetime import datetime

from fake_to_postgres.fake import create_fake_table
from fake_to_postgres.settings import (
    dsn,
    table_names,
    table_schemes_dict,
    conflict_fields,
)
from fake_to_postgres.write_to_postgres import write_to_postgres


def main():
    total_count = 0
    with psycopg2.connect(**dsn) as conn, conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor
    ) as cursor:
        for table_name in table_names:
            data_count = 0
            for data in create_fake_table(table_name):
                write_to_postgres(
                    data,
                    table_name,
                    table_schemes_dict[table_name],
                    conflict_fields[table_name],
                    conn,
                    cursor,
                )
                data_count += len(data)
            total_count += data_count
            print(f"В {table_name} загружено {data_count} записей.")
    conn.close()
    print(f"Всего загружено {total_count} записей.")


if __name__ == "__main__":
    start = datetime.now()
    main()
    end = datetime.now() - start
    total = round(end.total_seconds())
    print(f"Общее время формирования и загрузки записей: {total} секунд.")
