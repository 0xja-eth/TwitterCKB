# config/config.py
import asyncio
import os
import ssl

import redis.asyncio as redis  # 使用 redis 库的 asyncio 版本
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
USERNAME = os.getenv('TWITTER_USERNAME', "")
EMAIL = os.getenv('TWITTER_EMAIL', "")
PASSWORD = os.getenv('TWITTER_PASSWORD', "")
HTTP_PROXY = os.getenv('HTTP_PROXY', "")
HTTPS_PROXY = os.getenv('HTTPS_PROXY', "")
COOKIE_PATH = "cookies.json"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "")
AI_TOKEN = os.getenv('AI_TOKEN', "")
REDIS_URL = os.getenv('REDIS_URL', "")
# 从环境变量读取 Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TLS = os.getenv("REDIS_TLS", "false").lower() == "true"
REDIS_SNI = os.getenv("REDIS_SNI", None)
OUR_ADDRESS = os.getenv("OUR_ADDRESS", "")


# 配置 SSL 和 SNI
ssl_context = None
if REDIS_TLS:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    if REDIS_SNI:
        ssl_context.check_hostname = True
        # 在建立连接时，`redis-py` 会自动处理 SNI
        # 因此无需手动设置 `server_hostname`
        # 你只需要确保 SSLContext 配置正确即可

# 创建 Redis URL，根据是否启用 TLS 选择协议
protocol = "rediss" if REDIS_TLS else "redis"
redis_url = f"{protocol}://{REDIS_HOST}:{REDIS_PORT}"

# 创建异步 Redis 客户端
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


# # 创建异步 Redis 连接
# redis_client = redis.from_url(REDIS_URL)
