from twitter.client import client


async def post_tweet(content, image_paths=None):
    if image_paths:
        media_ids = [await client.upload_media(path) for path in image_paths]
        await client.create_tweet(text=content, media_ids=media_ids)
    else:
        await client.create_tweet(text=content)
    print("tweet send successfully")

