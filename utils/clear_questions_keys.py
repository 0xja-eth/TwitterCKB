# ./utils/clear_questions_keys.py
import asyncio
from config.config import redis_client


async def clear_question_keys():
    """
    Clears all Redis keys starting with 'question:'.
    """
    try:
        # Fetch all keys starting with 'question:'
        keys = await redis_client.keys("question:*")

        if not keys:
            print("No keys found with prefix 'question:'.")
            return

        # Delete all matching keys
        await redis_client.delete(*keys)
        print(f"Successfully cleared {len(keys)} keys with prefix 'question:'.")
    except Exception as e:
        print(f"Error clearing keys with prefix 'question:': {e}")

# Example of usage
if __name__ == "__main__":
    asyncio.run(clear_question_keys())
