import time
import psycopg2
import os
from typing import NoReturn


def wait_for_postgres() -> NoReturn:
    db_name = os.environ.get("POSTGRES_DB", "application_db")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = os.environ.get("POSTGRES_SERVER", "db")

    while True:
        try:
            # First connect to default database
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if our database exists
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cursor.fetchone() is None:
                # Create database if it doesn't exist
                print(f"Creating database {db_name}")
                cursor.execute(f'CREATE DATABASE "{db_name}"')
            
            cursor.close()
            conn.close()

            # Now try connecting to our actual database
            conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host
            )
            conn.close()
            break
            
        except psycopg2.OperationalError as e:
            print(f"Postgres is unavailable - sleeping: {e}")
            time.sleep(1)

    print("Postgres is up - continuing...")


if __name__ == "__main__":
    wait_for_postgres() 