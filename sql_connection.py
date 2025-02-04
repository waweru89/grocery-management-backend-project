import psycopg2
import os

__cnx = None

def get_sql_connection():
    global __cnx

    if __cnx is None:
        try:
            print("Opening PostgreSQL connection")
            __cnx = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                database=os.getenv('POSTGRES_DB')
            )
            print("Successfully connected to the database.")
        except psycopg2.Error as err:
            print(f"Error: {err}")
            return None

    return __cnx
