import asyncio
import aiohttp
from dotenv import load_dotenv
from config.config import AI_TOKEN

BASE_URL = "https://p01--ai-ckb-backend--bcdjt922dnwt.code.run"


async def fetch_balance():
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/balance"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return int(data["balance"])
            else:
                print(f"Failed to fetch balance, status code: {response.status}")
                return 0


async def transfer_ckb(to_address: str, amount_in_ckb: int):
    """Transfers CKB to the specified address."""
    url = f"{BASE_URL}/transfer"
    headers = {"Authorization": AI_TOKEN}
    payload = {
        "toAddress": to_address,
        "amountInCKB": str(amount_in_ckb)
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()

                # print successfully!!!
                print("\n" + "=" * 30)
                print("✅  Tweet sent successfully")
                print("=" * 30 + "\n")

                return f"Transfer successfully! your txHash is {data['txHash']}"
            else:
                print(f"Failed to transfer CKB, status code: {response.status}")
                return None
