# utils/input_util.py
import asyncio

input_queue = asyncio.Queue()


async def ainput(prompt: str = ""):
    """Asynchronous input function."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)