from energytt_platform.sql import SqlEngine

from .config import SQL_URI, SQL_POOL_SIZE


db = SqlEngine(
    uri=SQL_URI,
    pool_size=SQL_POOL_SIZE,
)
