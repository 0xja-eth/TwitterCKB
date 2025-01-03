# config/config.py
import asyncio
import os
import ssl

import redis.asyncio as redis  # use redis
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
USERNAME = os.getenv('TWITTER_USERNAME', "")
EMAIL = os.getenv('TWITTER_EMAIL', "")
PASSWORD = os.getenv('TWITTER_PASSWORD', "")
HTTP_PROXY = os.getenv('HTTP_PROXY', None)
HTTPS_PROXY = os.getenv('HTTPS_PROXY', None)
COOKIE_PATH = ""
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "")
AI_TOKEN = os.getenv('AI_TOKEN', "")
REDIS_URL = os.getenv('REDIS_URL', "")
# load redis from localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TLS = os.getenv("REDIS_TLS", "false").lower() == "true"
REDIS_SNI = os.getenv("REDIS_SNI", None)
OUR_ADDRESS = os.getenv("OUR_ADDRESS", "")
# load cookies
COOKIES_JSON = os.getenv("COOKIES_JSON")

# load price scope from localhost
CKB_MIN = int(os.getenv("CKB_MIN", 61))
CKB_MAX = int(os.getenv("CKB_MAX", 690))

SEAL_MIN = int(os.getenv("SEAL_MIN", 1))
SEAL_MAX = int(os.getenv("SEAL_MAX", 10))
SEAL_XUDT_ARGS = os.getenv("SEAL_XUDT_ARGS", "")

MIN_AWARD_SCORE = int(os.getenv("MIN_AWARD_SCORE", 85))

# set SSL 和 SNI
ssl_context = None
if REDIS_TLS:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    if REDIS_SNI:
        ssl_context.check_hostname = True

protocol = "rediss" if REDIS_TLS else "redis"
redis_url = f"{protocol}://{REDIS_HOST}:{REDIS_PORT}"

redis_client = redis.from_url(
    redis_url,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
)


async def check_redis_connection():
    try:
        await redis_client.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

if __name__ == "__main__":
    asyncio.run(check_redis_connection())

