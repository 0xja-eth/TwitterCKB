# openai_api/emoticon_gen.py
import json
import re

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
            1. "tweet_prefix": The prefix of the tweet, a creative introduction (5-20 words) describing 🦭.ai's current mood or vibe.
            2. "tweet_content": The main content of the tweet, A playful and expressive update (10-40 characters) on 🦭.ai’s mood, using emoticons to add fun and personality.
            
            Remember, only output the JSON object, nothing else.
            
            Here are a few example:
            
            {
                "tweet_prefix": "Drifting through the day, feeling light and free as a fish!",
                "tweet_content": "🎃Floating in a sea of calm and joy 💧🦭🌊"
            }
            
            {
            "tweet_prefix": "Today’s waves feel smooth and the ocean’s calling for a happy seal dance!",
            "tweet_content": "🐟💃 Dancing like no one’s watching 🦭🌊💦"
            }
            
            {
            "tweet_prefix": "The ocean is sparkling, and my fins are ready for a joyful swim!",
            "tweet_content": "💙🦭 Full of energy and splashing around 🌊🐠"
            }
            
            {
            "tweet_prefix": "Happy, peace and love!"
            "tweet_content": "🌊🦭 Feeling totally at peace with the tides 💙🐟"
            }
            
            """
            },
            {"role": "user", "content": "Please generate a fun and expressive tweet describing 🦭.ai's current mood as specified."}
        ]
    )
    content = response.choices[0].message.content

    # Parse the content as JSON
    try:
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        tweet_data = json.loads(cleaned_content)
        return tweet_data
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None
