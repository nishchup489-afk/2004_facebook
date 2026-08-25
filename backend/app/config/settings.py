from psycopg_pool import ConnectionPool 

from .config import DATABASE_URL


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
)