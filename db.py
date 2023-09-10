from psycopg2 import pool

# Initialize a connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1, maxconn=10,
    user="postgres",
    password="1234",
    host="localhost",
    port="5432",
    database="Goldenline_new"
)


def get_db_connection():
    return db_pool.getconn()


def release_db_connection(conn):
    db_pool.putconn(conn)
