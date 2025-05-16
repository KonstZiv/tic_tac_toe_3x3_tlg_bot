from psycopg import OperationalError
from .connection import create_connection
from tg_front.settings import Settings


def execute_query(settings: Settings, query: str):
    try:
        with create_connection(settings) as conn:
            conn.execute(query)
            conn.commit()
            print("Query executed.")
    except OperationalError as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    settings = Settings()
    print(settings)
    query = """
    CREATE TABLE IF NOT EXISTS message (
        id SERIAL PRIMARY KEY,
        text TEXT,
        user_id BIGINT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    execute_query(settings, query)
