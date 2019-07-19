from decouple import config

DEV_MODE = config("development", cast=bool)
MONGO_URI = config("mongo_uri")
HOST = config("host")
SECRET = config("secret")
WEBHOOK_URL = config("webhook_url")
GOOGLE_MAPS_API = config("google_maps_api")
GOOGLE_ANDROID_LOGIN_ID = config("google_android_login_id")
GOOGLE_IOS_LOGIN_ID = config("google_ios_login_id")


