# twitter/tweet.py
from twitter.client import client, login


async def post_tweet(content, image_paths=None):
    await login()  # Ensure login first
    try:
        if image_paths:
            media_ids = [await client.upload_media(path) for path in image_paths]
            await client.create_tweet(text=content, media_ids=media_ids)
        else:
            await client.create_tweet(text=content)
        # print successfully!!!
        print("\n" + "=" * 30)
        print("Tweet sent successfully")
        print("=" * 30 + "\n")
    except Exception as e:
        print("\n" + "=" * 30)
        print(f"Tweet send failed, please try again later: {e}")
        print("=" * 30 + "\n")

