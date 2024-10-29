# openai_api
from openai import OpenAI

from config.config import OPENAI_API_KEY

ai_client = OpenAI(api_key=OPENAI_API_KEY)
