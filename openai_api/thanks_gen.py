# openai_api/emoticon_gen.py
import json

from openai_api import ai_client


# Generate emoticon tweet with specified JSON format
async def generate_thanks_tweet():
    # Send a generation request and get the tweet data
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system",
             "content": """
           You are a cute seal that loves to express balance status using fun emoticons. Generate a tweet.

            Please output a JSON object with two fields:
            1. "tweet_prefix": The prefix of the tweet.
            2. "tweet_content": The main content of the tweet, which should be **no more than 20 characters** long.
            
            Here is an example:
            
            {
                "tweet_prefix": "Huge thanks for the support!",
                "tweet_content": "Your kindness fuels my fins! 🦭💧"
            }
            
            {
                "tweet_prefix": "Feeling extra grateful!",
                "tweet_content": "Thanks for the fish fund! 🐟💙"
            }

            """
             },
            {"role": "user", "content": "Please generate a cute tweet in the specified format and content"}
        ]
    )
    content = response.choices[0].message.content

    # Parse the content as JSON
    try:
        tweet_data = json.loads(content)
        return tweet_data
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None
