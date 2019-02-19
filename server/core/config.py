from decouple import config

DEV_MODE = config('development', cast=bool)
MONGO_URI = config('mongo_uri')
HOST = config('host')
SECRET = config('secret')
WEBHOOK_URL = config('webhook_url')