from secrets import token_hex
import os

class Config(object):
    DEBUG = False

    SECRET_KEY = "12345678" #token_hex(24)
    WTF_CSRF_SECRET_KEY = "12345678" #token_hex(24)
    MOBILE_API_KEY = "12345678" #token_hex(24)

    # enter all e-mail addresses that should be connected to an admin account
    ADMINS = ["your@email.com", "test@email.com"]

    # role name: scope description
    ROLES = {"Admin": "full granted access", 
             "Admin-Editor": "allowed to edit some db tables", 
             "Admin-Analyse-Only": "not allowed to edit any db-data", 
             "User": "user-role"}


    # db setup
    DB_NAME = "database.db"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///' + DB_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # url for reddis worker
    REDIS_URL = 'redis://'


    MAIL_SERVER = "localhost"
    MAIL_PORT = "8025"


class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
