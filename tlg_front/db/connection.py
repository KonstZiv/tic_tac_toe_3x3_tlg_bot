from psycopg import connect, OperationalError

from settings import Settings


def create_connection(settings_: Settings):
    try:
        connection = connect(
            host=settings_.POSTGRES_HOST,
            dbname=settings_.POSTGRES_DB,
            user=settings_.POSTGRES_USER,
            password=settings_.POSTGRES_PASSWORD
        )
        print("Connection established.")
        return connection
    except OperationalError as e:
        print(f"Error: {e}")
        raise
