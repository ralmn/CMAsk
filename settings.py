DEBUG = False
SECRET_KEY = 'something secret'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

REDIS_CHAN = 'cmask'

BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

CELERY_BROKER_URL=BROKER_URL
CELERY_RESULT_BACKEND=BROKER_URL

 # Configure Flask-User
USER_LOGIN_URL              = "/login"
USER_REGISTER_URL           = "/register"
USER_UNAUTHORIZED_URL     = '/unauthorized'

# Configure Flask-Mail -- Required for Confirm email and Forgot password features
MAIL_SERVER   = ''
MAIL_PORT     = 25
MAIL_USE_SSL  = False                            # Some servers use MAIL_USE_TLS=True instead
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = '"'

SOCKET_HOST = '127.0.0.1:8000'


#SQLLite : "sqlite:////home/path/of/database"
#MySQL : "mysql://user:pass@127.0.0.1/base"
SQLALCHEMY_DATABASE_URI = ''
