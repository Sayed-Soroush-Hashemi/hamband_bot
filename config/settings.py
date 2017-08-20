from sqlalchemy import create_engine

token_file = open('config/token.txt', 'r')
TOKEN = token_file.read()
token_file.close()
del token_file

DB = {
    'DRIVER': 'postgresql',
    'NAME': 'hamband_bot_db',
    'USER': 'hamband_bot',
    'PASSWORD': open('config/db_password.txt', 'r').read(),
    'HOST': 'localhost',
    'PORT': '5432'
}
engine = create_engine('{0}://{1}:{2}@{3}:{4}/{5}'.format(
    DB['DRIVER'], DB['USER'], DB['PASSWORD'], DB['HOST'], DB['PORT'], DB['NAME']
))
con = engine.connect()

POLLING_SLEEP_TIME = 0.005
