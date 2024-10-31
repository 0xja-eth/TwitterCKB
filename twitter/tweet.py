# twitter/tweet.py
import asyncio
import base64
import os
from datetime import datetime

from ckb.ckb_service import transfer_ckb, transfer_token
from config.config import redis_client, SEAL_XUDT_ARGS, CKB_MIN, CKB_MAX, SEAL_MAX, SEAL_MIN
from openai_api.award_gen import analyze_reply_for_transfer
from twitter.client import client, login
import time

# Global variable to stop the loop
fetch_and_analyze_stop_event = asyncio.Event()
is_fetch_and_analyze_active = False


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
        return True
    except Exception as e:
        print("\n" + "=" * 30)
        print(f"Tweet send failed, please try again later: {e}")
        print("=" * 30 + "\n")
        return False


async def fetch_and_analyze_replies(user_id):
    await login()
    # Define an initial timestamp set to a year in the past
    initial_timestamp = datetime.now().timestamp() - 365 * 24 * 60 * 60

    while not fetch_and_analyze_stop_event.is_set():
        if os.getenv("IS_TRANSFER", "False").lower() != "true" or not is_fetch_and_analyze_active:
            print("Transfer environment setting or fetch mode is disabled. Pausing task.")
            await asyncio.sleep(15)  # Wait before rechecking
            return

        try:
            tweets = await client.get_user_tweets(user_id, "Tweets")
            await asyncio.sleep(1)
            for tweet in tweets:
                tweet_id = tweet.id
                tweet = await client.get_tweet_by_id(tweet_id)
                await asyncio.sleep(1)
                replies_count = tweet.reply_count
                now_count = 0

                last_processed_time = await redis_client.get(f"last_processed_time:{tweet_id}")
                await asyncio.sleep(1)
                if not last_processed_time:
                    last_processed_time = initial_timestamp
                    await redis_client.set(f"last_processed_time:{tweet_id}", last_processed_time)
                else:
                    last_processed_time = float(last_processed_time)

                replies = tweet.replies

                while replies:
                    for reply in replies:
                        if not is_fetch_and_analyze_active:
                            return
                        reply_timestamp = reply.created_at_datetime.timestamp()

                        # Skip replies processed previously
                        if reply_timestamp <= float(last_processed_time):
                            now_count += 1
                            # print(now_count)
                            continue

                        print("Reply:", reply.full_text)

                        # analyze and process comment
                        response = await analyze_reply_for_transfer(reply.full_text)

                        # Check if an address and amount are present
                        to_address = response.get("to_address")
                        amount = response.get("amount")
                        currency_type = response.get("currency_type")

                        # just for test
                        # if to_address and amount and currency_type:
                        #     if currency_type == "CKB":
                        #         if CKB_MIN <= amount <= CKB_MAX:
                        #             transfer_result = await transfer_ckb(to_address, amount)
                        #     elif currency_type == "Seal":
                        #         if SEAL_MIN <= amount <= SEAL_MAX:
                        #             transfer_result = await transfer_token(to_address, amount, SEAL_XUDT_ARGS)
                        #     else:
                        #         print("Unrecognized currency type in response:", currency_type)
                        #         continue

                            # print("Transfer Result:", transfer_result)

                        # Update last processed time
                        last_processed_time = reply_timestamp
                        await redis_client.set(f"last_processed_time:{tweet_id}", last_processed_time)
                        await asyncio.sleep(1)
                        now_count += 1
                    if not is_fetch_and_analyze_active:
                        return
                    if replies.next and now_count <= replies_count:
                        try:
                            replies = await replies.next()
                            await asyncio.sleep(20)
                        except Exception as e:
                            print(f"replies.next() error: {e} ")
                            break
                    else:
                        break  # if no more, break it
            await asyncio.sleep(60)
        except Exception as e:
            print("\n" + "=" * 30)
            print(f"Failed to retrieve replies: {e}")
            print("=" * 30 + "\n")
            continue


def get_is_fetch_and_analyze_active():
    return is_fetch_and_analyze_active


def set_is_fetch_and_analyze_active(is_fetch):
    global is_fetch_and_analyze_active
    is_fetch_and_analyze_active = is_fetch
