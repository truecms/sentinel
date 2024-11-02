import time
import psycopg2
import os
from typing import NoReturn


def wait_for_postgres() -> NoReturn:
    while True:
        try:
            psycopg2.connect(
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                host=os.environ["POSTGRES_SERVER"],
            )
            break
        except psycopg2.OperationalError:
            print("Postgres is unavailable - sleeping")
            time.sleep(1)

    print("Postgres is up - continuing...")


if __name__ == "__main__":
    wait_for_postgres() 