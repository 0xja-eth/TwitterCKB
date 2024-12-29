# ckb/ckb_service.py
import asyncio
import os

import aiohttp
from dotenv import load_dotenv
from config.config import AI_TOKEN, SEAL_XUDT_ARGS
from config.logging_config import logger

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


async def fetch_invoice_detail(invoice: str):
    """
    Fetch and validate a Fiber invoice.

    :param invoice: The Fiber invoice string to validate
    :return: JSON response with invoice details or None if the request fails
    """
    url = f"{BASE_URL}/fiber/invoice"
    headers = {"Authorization": AI_TOKEN}  # Add authorization header if required
    params = {"invoice": invoice}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print("\n" + "=" * 30)
                print("Fetched Invoice Details Successfully")
                print("=" * 30 + "\n")
                return data
            else:
                print(f"Failed to fetch invoice details, status code: {response.status}")
                logger.info(f"Failed to fetch invoice details, status code: {response.status}")
                return None


async def transfer_ckb_with_invoice(invoice: str, amount_in_ckb: int, channel_id=None):
    """
    Transfer CKB using a Fiber invoice.

    :param invoice: The Fiber invoice string
    :param amount_in_ckb: The amount to transfer in CKB
    :param channel_id: The channel ID associated with the transfer
    :return: JSON response with transfer details or None if the request fails
    """
    url = f"{BASE_URL}/fiber/transfer"
    headers = {"Authorization": AI_TOKEN}  # Authorization header
    payload = {
        "invoice": invoice,
        "amountInCKB": amount_in_ckb,
        "channelId": channel_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print("\n" + "=" * 30)
                print("Transfer CKB using Fiber Invoice Successful")
                logger.info("Transfer CKB using Fiber Invoice Successful")
                print("=" * 30 + "\n")
                return data
            else:
                print(f"Failed to transfer CKB, status code: {response.status}")
                logger.info(f"Failed to fetch invoice details, status code: {response.status}")
                return None

if __name__ == "__main__":
    asyncio.run(transfer_token("12314134", 10))
