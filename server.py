# server.py

import asyncio
import json
import os
import sys
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from config.config import redis_client, OUR_ADDRESS
from openai_api.chat import chat_with_openai, send_emoticon_tweet, send_thanks_tweet
from openai_api.thanks_gen import generate_thanks_tweet
from twitter.tweet import fetch_and_analyze_replies, get_is_fetch_and_analyze_active, set_is_fetch_and_analyze_active, \
    fetch_and_analyze_stop_event
from twitter.tweet_for_question import set_is_tweet_for_question_active, get_is_tweet_for_question_active, \
    tweet_for_question_stop_event
from utils.emoticon import generate_balance_emoticon

app = FastAPI()

# Define a global stop event for the status update thread
stop_event = threading.Event()
transaction_stop_event = asyncio.Event()
is_status_update_running = False
is_transaction_listener_running = False

class ChatRequest(BaseModel):
    message: str


class FetchAndAnalyzeRepliesRequest(BaseModel):
    user_id: str


async def listen_for_transactions():
    """
    Continuously listen for new transactions in the Redis sorted set 'transaction_hash'.
    When a new txHash is found, retrieve transaction data from 'transactions' HASH,
    check balance changes, and send thank-you tweet if applicable.
    Implement logical deletion by marking transactions as processed.
    """
    global is_transaction_listener_running
    if not OUR_ADDRESS:
        print("OUR_ADDRESS not set in environment variables.")
        return
    try:
        while not transaction_stop_event.is_set():
            try:
                # Get all txHashes
                tx_hashes = await redis_client.zrange("transaction_hash", 0, -1)
                for tx_hash in tx_hashes:
                    tx_hash = tx_hash.decode("utf-8")
                    # Get tx_data from tx_hash
                    tx_data = await redis_client.hget("transactions", tx_hash)
                    post_result = False
                    if tx_data:
                        try:
                            tx_data = json.loads(tx_data.decode("utf-8"))
                        except json.JSONDecodeError:
                            print(f"Failed to decode transaction data for txHash: {tx_hash}")
                            # tag as processed
                            updated_tx_data = {"processed": True, "error": "Invalid JSON"}
                            await redis_client.hset("transactions", tx_hash, json.dumps(updated_tx_data))
                            continue

                        # check if deal
                        if tx_data.get("processed", False):
                            continue

                        balance_changes = tx_data.get("balanceChanges", [])
                        for change in balance_changes:
                            if change.get("address") == OUR_ADDRESS and int(change.get("value", "0")) > 0:
                                inputs = tx_data.get("inputs", [])
                                sender_addresses = [inp.get("address") for inp in inputs if inp.get("address")]
                                if sender_addresses:
                                    sender = sender_addresses[0]
                                    print(f"Detected transfer from {sender} to {OUR_ADDRESS}, txHash: {tx_hash}")

                                    response, post_result = await send_thanks_tweet(sender, int(change.get("value", "1")))
                                    await asyncio.sleep(8)
                                    print(f"Thank-you tweet response: {response}")
                                else:
                                    print(f"🔍 No sender address found in transaction {tx_hash}")
                        if post_result:
                            tx_data['processed'] = True
                            await redis_client.hset("transactions", tx_hash, json.dumps(tx_data))
                    else:
                        print(f"No transaction data found for txHash: {tx_hash}")
            except Exception as e:
                print(f"Error in listen_for_transactions: {e}")
            await asyncio.sleep(15)
    except Exception as e:
        print(f"Error in listen_for_transactions: {e}")
    finally:
        is_transaction_listener_running = False  # Reset flag on exit


# Function to send emoticon tweets at intervals, runs in a separate thread
def schedule_emoticon_tweet_thread():
    global is_status_update_running
    tweet_interval = 3600  # Send a tweet every hour
    last_tweet_time = time.time()

    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initial send
    loop.run_until_complete(send_emoticon_tweet())

    while not stop_event.is_set():
        try:
            current_time = time.time()
            if current_time - last_tweet_time >= tweet_interval:
                loop.run_until_complete(send_emoticon_tweet())
                last_tweet_time = current_time  # Update last send time
            # Check stop event every second
            time.sleep(1)
        except Exception as e:
            print(f"Error in schedule_emoticon_tweet_thread: {e}")
            break
    print("Stopped schedule_emoticon_tweet_thread.")
    is_status_update_running = False  # Reset flag on exit


@app.post("/start_listen_transactions")
async def start_listen_transactions(background_tasks: BackgroundTasks):
    global is_transaction_listener_running
    if is_transaction_listener_running:
        return {"status": 400, "message": "Transaction listener is already running."}
    is_transaction_listener_running = True
    transaction_stop_event.clear()  # Ensure previous stop event is cleared
    background_tasks.add_task(listen_for_transactions)
    return {"status": 200, "message": "Transaction listener started successfully."}


@app.post("/stop_listen_transactions")
async def stop_listen_transactions():
    global is_transaction_listener_running
    if not is_transaction_listener_running:
        return {"status": 400, "message": "Transaction listener is not running."}
    transaction_stop_event.set()  # Signal to stop the listener
    is_transaction_listener_running = False
    return {"status": 200, "message": "Transaction listener stopped successfully."}


# Server Service with no chat, it just processes some schedule tasks, but if u want to chat, u can deploy it yourself
# @app.post("/chat")
# async def chat_with_ai(request: ChatRequest):
#     """
#     Chat endpoint to interact with OpenAI chat.
#     :param message: The message to send to the OpenAI chat API.
#     """
#     response = await chat_with_openai(request.message)
#     return {"status": 200, "msg": "success", "response": response}


@app.post("/status_update/start")
async def start_status_update_mode(background_tasks: BackgroundTasks):
    """
    Start the status update mode as a background task.
    """
    global is_status_update_running
    if is_status_update_running:
        return {"status": 400, "message": "Status update mode is already running."}
    is_status_update_running = True
    stop_event.clear()  # Ensure stop event is clear to allow thread to start
    thread = threading.Thread(target=schedule_emoticon_tweet_thread)
    thread.start()
    background_tasks.add_task(thread.join)  # Ensure thread is cleaned up if needed
    return {"status": 200, "message": "success"}


@app.post("/status_update/stop")
async def stop_status_update_mode():
    global is_status_update_running
    if not is_status_update_running:
        return {"status": 400, "message": "Status update mode is not running."}
    stop_event.set()
    is_status_update_running = False
    return {"status": 200, "message": "success"}


@app.post("/fetch_and_analyze_replies")
async def fetch_and_analyze_replies_mode(request: FetchAndAnalyzeRepliesRequest, background_tasks: BackgroundTasks):
    is_fetch_and_analyze_active = get_is_fetch_and_analyze_active()
    if os.getenv("IS_TRANSFER", "False").lower() == "true" and is_fetch_and_analyze_active:
        background_tasks.add_task(fetch_and_analyze_replies, request.user_id)
        return {"status": 200, "message": "success"}
    else:
        return {"status": 403, "message": "success", "data": "Transfers are disabled by system settings."}


@app.post("/start_fetch_and_analyze")
async def start_fetch_and_analyze_mode():
    if os.getenv("IS_TRANSFER", "False").lower() != "true":
        return {"status": 403, "message": "Transfers are disabled by system environment setting."}

    set_is_fetch_and_analyze_active(True)
    fetch_and_analyze_stop_event.clear()  # Clear stop event to start task
    return {"status": 200, "message": "Fetch and analyze mode started successfully."}


@app.post("/stop_fetch_and_analyze")
async def stop_fetch_and_analyze_mode():
    set_is_fetch_and_analyze_active(False)
    fetch_and_analyze_stop_event.set()  # Set stop event to pause task
    return {"status": 200, "message": "Fetch and analyze mode stopped successfully."}


@app.post("/start_tweet_for_question")
async def start_tweet_for_question_mode():
    if os.getenv("IS_TRANSFER", "False").lower() != "true":
        return {"status": 403, "message": "Transfers are disabled by system environment setting."}

    set_is_tweet_for_question_active(True)
    tweet_for_question_stop_event.clear()
    return {"status": 200, "message": "Tweet for question mode started successfully."}


@app.post("/fetch_and_analyze_question_replies")
async def fetch_and_analyze_question_replies(background_tasks: BackgroundTasks):
    is_tweet_for_question_active = get_is_tweet_for_question_active()
    if os.getenv("IS_TRANSFER", "False").lower() == "true" and is_tweet_for_question_active:
        background_tasks.add_task(fetch_and_analyze_replies)
        return {"status": 200, "message": "success"}
    else:
        return {"status": 403, "message": "success", "data": "Transfers are disabled by system settings."}


@app.post("/stop_tweet_for_question")
async def stop_tweet_for_question_mode():
    set_is_tweet_for_question_active(False)
    tweet_for_question_stop_event.set()  # Set stop event to pause task
    return {"status": 200, "message": "Fetch and analyze mode stopped successfully."}
