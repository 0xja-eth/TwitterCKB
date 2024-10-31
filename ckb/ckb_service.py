# ckb/ckb_service.py
import asyncio
import os

import aiohttp
from dotenv import load_dotenv
from config.config import AI_TOKEN, SEAL_XUDT_ARGS

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8081")


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


async def fetch_token_balance(xudt_args: str = SEAL_XUDT_ARGS):
    """Fetch the balance of a specified custom token (XUDT)."""
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/balance/{xudt_args}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return int(data["balance"])
            else:
                print(f"Failed to fetch token balance, status code: {response.status}")
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
                print("Transfer CKB successfully")
                print("=" * 30 + "\n")

                return f"Transfer successfully! your txHash is {data['txHash']}"
            else:
                print(f"Failed to transfer CKB, status code: {response.status}")
                return None


async def transfer_token(to_address: str, amount: int, xudt_args: str = SEAL_XUDT_ARGS):
    """Transfers a specified amount of a custom token (XUDT) to the specified address."""
    url = f"{BASE_URL}/transfer/{xudt_args}"
    headers = {"Authorization": AI_TOKEN}
    payload = {
        "toAddress": to_address,
        "amountInCKB": str(amount)  # "amountInCKB" here refers to the token amount unit
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print("Transfer Token successfully")
                return f"Transfer successfully! Your txHash is {data['txHash']}"
            else:
                print(f"Failed to transfer Token, status code: {response.status}")
                return None

if __name__ == "__main__":
    asyncio.run(transfer_token())
