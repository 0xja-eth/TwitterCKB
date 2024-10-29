import uuid
import aiohttp

from openai_api import ai_client


async def generate_image_from_text(description, num=1):
    response = ai_client.images.generate(model="dall-e-3", prompt=description, size="1024x1024", n=num)
    image_urls = response['data']
    image_paths = []

    async with aiohttp.ClientSession() as session:
        for url in image_urls:
            unique_filename = f"./images/{uuid.uuid4()}.jpg"
            async with session.get(url["url"]) as image_resp:
                if image_resp.status == 200:
                    with open(unique_filename, 'wb') as f:
                        f.write(await image_resp.read())
                    image_paths.append(unique_filename)
    return image_paths
