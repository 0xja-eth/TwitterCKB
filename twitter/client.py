# twitter/client.py
import json
import os
from twikit import Client
from config.config import EMAIL, USERNAME, PASSWORD, COOKIE_PATH, HTTP_PROXY, COOKIES_JSON

if HTTP_PROXY == "" or HTTP_PROXY is None:
    client = Client('en-US',
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')
else:
    client = Client('en-US', proxy=HTTP_PROXY,
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')

async def login():
    if os.path.exists(COOKIE_PATH) and os.path.getsize(COOKIE_PATH) > 0:
        client.load_cookies(COOKIE_PATH)
    elif COOKIES_JSON is not None and COOKIES_JSON != "":
        cookies = json.loads(COOKIES_JSON)
        client.set_cookies(cookies)
    else:
        await client.login(auth_info_1=EMAIL, auth_info_2=USERNAME, password=PASSWORD)
        client.save_cookies(COOKIE_PATH)
