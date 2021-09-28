import os


# Service description
TOKEN_SECRET = '54321'

# Event Bus
EVENT_BUS_HOST = os.environ.get('EVENT_BUS_HOST', 'localhost')
EVENT_BUS_PORT = int(os.environ.get('EVENT_BUS_PORT', 9092))
EVENT_BUS_SERVERS = [
    f'{EVENT_BUS_HOST}:{EVENT_BUS_PORT}',
]

# SQL
SQL_URI = os.getenv('SQL_URI', 'postgresql://postgres:1234@localhost:5432/meteringpoints')
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))
