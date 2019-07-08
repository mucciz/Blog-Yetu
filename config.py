class Config:
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://deathstar:deathstar@localhost/pitch'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SECRET_KEY = '4d7bb6b158565756'
    # RANDOM_QUOTES_BASE_URL = 'http://quotes.stormconsultancy.co.uk/random.json'

class ProdConfig(Config):
    pass

class TestConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True

config_options ={"production":ProdConfig,"default":DevConfig,"testing":TestConfig}