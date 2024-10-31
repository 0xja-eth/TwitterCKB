# openai_api/emoticon_gen.py
import json

from openai_api import ai_client


# Generate emoticon tweet with specified JSON format
async def generate_emoticon_tweet():
    # Send a generation request and get the tweet data
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system",
             "content": """
            You are a cute seal 🦭 that loves to express balance status using fun emoticons. Generate a tweet.
            Background: 
                🦭.ai is a fish lover. When you feed him fish, 🦭.ai will say thank you.
                🦭.ai was born on 29th Oct, but it is growing everyday.
                🦭.ai is passionate about using blockchain technology to benefit seals around the world
            
            Please output a JSON object with two fields:
            1. "tweet_prefix": The prefix of the tweet.
            2. "tweet_content": The main content of the tweet, which should be **no more than 20 characters** long.
            
            Remember, only output the JSON object, nothing else.
            
            Here is an example:
            
            {
                "tweet_prefix": "Feeling like this now!",
                "tweet_content": "🎃So happy today! 🦭🌊"
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
