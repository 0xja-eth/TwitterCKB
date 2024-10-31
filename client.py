# client.py
import asyncio
import os

import aiohttp

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8081")


async def start_listen_transactions():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/start_listen_transactions") as response:
            print(await response.json())


async def stop_listen_transactions():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/stop_listen_transactions") as response:
            print(await response.json())


async def start_status_update_mode():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/status_update/start") as response:
            print(await response.json())


async def stop_status_update_mode():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/status_update/stop") as response:
            print(await response.json())


async def chat_with_ai():
    print("Chat mode activated. Type your message or 'exit' to return to the main menu.")
    async with aiohttp.ClientSession() as session:
        while True:
            message = input("You: ")
            if message.lower() == "exit":
                print("Exiting chat mode.")
                break
            async with session.post(f"{BASE_URL}/chat", json={"message": message}) as response:
                try:
                    data = await response.json()
                    print("AI:", data.get("response", "Error in AI response"))
                except aiohttp.ContentTypeError:
                    print("Failed to get a valid JSON response from the server.")

async def start_fetch_and_analyze_mode():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/start_fetch_and_analyze") as response:
            print(await response.json())
async def stop_fetch_and_analyze_mode():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/stop_fetch_and_analyze") as response:
            print(await response.json())

async def fetch_and_analyze_replies():
    user_id = input("Please enter the twitter user_id that you would like to analyze:")
    async with aiohttp.ClientSession() as session:
        payload = {"user_id": user_id}
        async with session.post(f"{BASE_URL}/fetch_and_analyze_replies", json=payload) as response:
            print(await response.json())

async def main():
    while True:
        print("\nPlease select a mode:")
        print("1. Start Listening for Transactions")
        print("2. Stop Listening for Transactions")
        print("3. Start Status Update Mode")
        print("4. Stop Status Update Mode")
        print("5. Chat with AI")
        print("6. Start_fetch_and_analyze_mode")
        print("7. Stop_fetch_and_analyze_mode")
        print("8. Fetch_and_analyze_replies")
        print("9. Exiting client.")
        choice = input("Enter the number of your choice: ")

        if choice == '1':
            await start_listen_transactions()
        elif choice == '2':
            await stop_listen_transactions()
        elif choice == '3':
            await start_status_update_mode()
        elif choice == '4':
            await stop_status_update_mode()
        elif choice == '5':
            await chat_with_ai()
        elif choice == '6':
            await start_fetch_and_analyze_mode()
        elif choice == '7':
            await stop_fetch_and_analyze_mode()
        elif choice == '8':
            await fetch_and_analyze_replies()
        elif choice == '9':
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
