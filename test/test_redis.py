import asyncio

import redis

from config.config import check_redis_connection

# redis_client = redis.Redis(host='localhost', port=6379, db=0)
#
# try:
#     # 测试连接：插入一个键值对到 Redis
#     redis_client.set("test_key", "Hello, Redis!")
#
#     # 获取刚插入的值
#     value = redis_client.get("test_key")
#
#     # 显示结果
#     print("Inserted value:", value.decode("utf-8"))  # 解码为字符串
# except redis.exceptions.ConnectionError as e:
#     print("Could not connect to Redis:", e)
# except Exception as e:
#     print("An error occurred:", e)

asyncio.run(check_redis_connection())
