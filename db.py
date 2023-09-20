from psycopg2 import pool
import os

# Initialize a connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1, maxconn=10,
    user=os.environ.get('DBUSER'),
    password=os.environ.get('DBPASSWORD'),
    host=os.environ.get('DBHOST'),
    port=os.environ.get('DBPORT'),
    database=os.environ.get('DBNAME')
)


def get_db_connection():
    return db_pool.getconn()


def release_db_connection(conn):
    db_pool.putconn(conn)
