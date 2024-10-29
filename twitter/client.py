# twitter/client.py
import os
from twikit import Client
from config.config import EMAIL, USERNAME, PASSWORD, COOKIE_PATH, HTTP_PROXY

client = Client('en-US', proxy=HTTP_PROXY,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')


async def login():
    if os.path.exists(COOKIE_PATH) and os.path.getsize(COOKIE_PATH) > 0:
        client.load_cookies(COOKIE_PATH)
    else:
        await client.login(auth_info_1=EMAIL, auth_info_2=USERNAME, password=PASSWORD)
        client.save_cookies(COOKIE_PATH)
