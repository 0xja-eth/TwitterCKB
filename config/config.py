import os
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