import os


# -- General -----------------------------------------------------------------

# Secret used to sign internal token
INTERNAL_TOKEN_SECRET = os.environ.get('INTERNAL_TOKEN_SECRET', '')


# -- Message Bus -------------------------------------------------------------

# Message Bus host
MESSAGE_BUS_HOST = os.environ.get('MESSAGE_BUS_HOST', '')

# Message Bus post
MESSAGE_BUS_PORT = int(os.environ.get('MESSAGE_BUS_PORT', 9092))

# List of Message Bus servers
MESSAGE_BUS_SERVERS = [f'{MESSAGE_BUS_HOST}:{MESSAGE_BUS_PORT}']


# -- SQL ---------------------------------------------------------------------

# SqlAlchemy connection string
SQL_URI = os.environ.get('SQL_URI', '')

# Number of concurrent connection to SQL database
SQL_POOL_SIZE = int(os.getenv('SQL_POOL_SIZE', 1))
