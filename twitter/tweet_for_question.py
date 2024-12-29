# twitter/tweet_for_question.py
import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

from ckb.ckb_service import transfer_ckb, fetch_invoice_detail, transfer_ckb_with_invoice
from config.config import redis_client, CKB_MIN, CKB_MAX
from config.logging_config import logger
from openai_api.question_and_answer_gen import generate_question_with_answer, judge_answer_for_score
from twitter.new_client import n_client as client
from twitter.operations import post_tweet, get_user_mention_comments, reply_comment


# Global variables to control the process
tweet_for_question_stop_event = asyncio.Event()
is_tweet_for_question_active = False


def serialize_datetime(obj):
    """Convert datetime objects to ISO 8601 formatted strings for JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def deserialize_datetime(obj):
    """Convert JSON string fields into datetime objects."""
    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], str):
                try:
                    # Attempt to parse ISO 8601 strings into datetime
                    obj[key] = datetime.fromisoformat(obj[key])
                except ValueError:
                    continue
    return obj


async def tweet_for_question():
    user_id = client.api_client.get_me().data.id
    """
    Main function to handle posting questions, processing mentions, and rewarding answers.
    """
    while not tweet_for_question_stop_event.is_set():
        if os.getenv("IS_TRANSFER", "False").lower() != "true" or not is_tweet_for_question_active:
            print("Transfer environment setting or fetch mode is disabled. Pausing task.")
            logger.info("Transfer environment setting or fetch mode is disabled. Pausing task.")
            await asyncio.sleep(15)  # Wait before rechecking
            return

        try:
            # Step 1: Check for existing unanswered questions in Redis
            keys = await redis_client.keys("question:*")
            existing_question_key = None

            for key in keys:
                question_metadata = json.loads(await redis_client.get(key))
                if not question_metadata.get("rewarded", False):
                    existing_question_key = key
                    break

            if existing_question_key:
                print(f"Found an existing unanswered question: {existing_question_key}")
                logger.info(f"Found an existing unanswered question: {existing_question_key}")
                question_metadata = json.loads(await redis_client.get(existing_question_key), object_hook=deserialize_datetime)
                question_context = question_metadata["context"]
                question_prompt = question_metadata["prompt"]
                reference_answer = question_metadata["reference_answer"]
                amount = question_metadata["amount"]
                timestamp = question_metadata["timestamp"]
                question_key = existing_question_key

                # Check if the question has exceeded 3 hours
                if datetime.now(timezone.utc) - timestamp > timedelta(hours=3):
                    print(f"Question {existing_question_key} has expired (3 hours exceeded). Marking as rewarded.")
                    logger.info(
                        f"Question {existing_question_key} has expired (3 hours exceeded). Marking as rewarded.")
                    question_metadata["rewarded"] = True
                    await redis_client.set(existing_question_key,
                                           json.dumps(question_metadata, default=serialize_datetime))
                    continue

            else:
                # Step 1: Generate a question and reference answer
                question_data = await generate_question_with_answer()
                if not question_data:
                    print("Failed to generate question and answer. Retrying...")
                    logger.info("Failed to generate question and answer. Retrying...")
                    await asyncio.sleep(60)
                    continue

                question_context = question_data["question_context"]
                question_prompt = question_data["question_prompt"]
                reference_answer = question_data["reference_answer"]
                amount = question_data["amount"]
                timestamp = datetime.now(timezone.utc)
                # Combine question context and prompt for the tweet
                # Combine question context, prompt, and amount for the tweet
                tweet_content = (
                    f"{question_context}\n\n"
                    f"🔍 {question_prompt}\n\n"
                    f"💰 Reward: {amount} CKB for the best answer! 🎉"
                )
                tweet_response = post_tweet(client, tweet_content)

                if not tweet_response:
                    print("Failed to post the question. Retrying...")
                    logger.info("Failed to post the question. Retrying...")
                    await asyncio.sleep(60)
                    continue

                tweet_id = tweet_response["tweet_id"]
                print(f"Tweet posted successfully: {tweet_id}")
                logger.info(f"Tweet posted successfully: {tweet_id}")

                # Store the question metadata in Redis
                question_key = f"question:{tweet_id}"
                question_metadata = {
                    "context": question_context,
                    "prompt": question_prompt,
                    "reference_answer": reference_answer,
                    "amount": amount,
                    "timestamp": timestamp,
                    "rewarded": False,
                    "last_processed_timestamp": None
                }
                await redis_client.set(question_key, json.dumps(question_metadata, default=serialize_datetime))

            # Step 2: Fetch mentions and process comments
            while not tweet_for_question_stop_event.is_set():
                if not is_tweet_for_question_active:
                    return
                question_metadata = json.loads(await redis_client.get(question_key), object_hook=deserialize_datetime)
                if question_metadata["rewarded"]:
                    break  # If the question has already been rewarded, stop processing this question

                last_processed_timestamp = question_metadata.get("last_processed_timestamp")
                if not last_processed_timestamp:
                    # Default to three months ago for the initial fetch
                    last_processed_timestamp = datetime.now(timezone.utc) - timedelta(days=90)

                # Fetch mentions since the last processed timestamp
                mentions = get_user_mention_comments(
                    client,
                    user_id=user_id,
                    start_time=last_processed_timestamp,
                    max_results=5
                )

                # Check if the question has exceeded 3 hours
                if datetime.now(timezone.utc) - timestamp > timedelta(hours=3):
                    print(f"Question {existing_question_key} has expired (3 hours exceeded). Marking as rewarded.")
                    logger.info(
                        f"Question {existing_question_key} has expired (3 hours exceeded). Marking as rewarded.")
                    question_metadata["rewarded"] = True
                    await redis_client.set(existing_question_key,
                                           json.dumps(question_metadata, default=serialize_datetime))
                    break

                if not mentions:
                    print("No new mentions found. Retrying...")
                    await asyncio.sleep(30)
                    continue

                if mentions.data is None:
                    print("No new mentions found. Retrying...")
                    await asyncio.sleep(360)
                    continue

                for mention in mentions.data:
                    if not is_tweet_for_question_active:
                        return
                    mention_text = mention.text
                    mention_id = mention.id

                    logger.info(f"mention_text: {mention_text} mention_id: {mention_id}")

                    # Step 3: Evaluate mention using judge_answer_for_score
                    result = await judge_answer_for_score(
                        question_context=question_context,
                        question_prompt=question_prompt,
                        reference_answer=reference_answer,
                        user_answer=mention_text
                    )

                    score = result.get("score", 0)
                    invoice = result.get("invoice", None)
                    reply_content = result.get("reply_content", None)

                    if score >= 50:  # Only reward if the score is >= 50
                        if invoice and amount:
                            # Mark the question as rewarded in Redis
                            question_metadata["rewarded"] = True

                            # TODO finish transfer logic
                            # data = await fetch_invoice_detail(invoice)
                            # if data:
                            #     response = None
                            #     if CKB_MIN <= amount <= CKB_MAX:
                            #         response = await transfer_ckb_with_invoice(invoice, amount)
                            #     if response:
                            #         # Reply and acknowledge the user's response
                            #         reply_content = reply_content
                            #         reply_comment(client, mention_id, reply_content)
                            #         await redis_client.set(question_key,
                            #                                json.dumps(question_metadata, default=serialize_datetime))
                            #         print(f"Rewarded user with invoice {invoice} for {amount} in CKB")

                            # Reply and acknowledge the user's response
                            reply_content = reply_content
                            reply_comment(client, mention_id, reply_content)
                            await redis_client.set(question_key, json.dumps(question_metadata, default=serialize_datetime))
                            print(f"Rewarded user with invoice {invoice} for {amount} in CKB")

                            break  # Move to the next question after rewarding
                        else:
                            # Reply without rewarding if no valid address or amount
                            reply_content = reply_content
                            reply_comment(client, mention_id, reply_content)
                            print(f"Send response: {reply_content}")
                    else:
                        print(f"Low quality answer from mention ID {mention_id}, not rewarded.")

                # Update the last processed timestamp in Redis
                question_metadata["last_processed_timestamp"] = datetime.now(timezone.utc)
                await redis_client.set(question_key, json.dumps(question_metadata, default=serialize_datetime))
                if not is_tweet_for_question_active:
                    return
                await asyncio.sleep(360)  # Pause between fetches
            if not is_tweet_for_question_active:
                return
            await asyncio.sleep(600)

        except Exception as e:
            logger.error(f"Error in tweet_for_question: {e}")
            print(f"Error in tweet_for_question: {e}")
            await asyncio.sleep(60)  # Pause before retrying


def get_is_tweet_for_question_active():
    return is_tweet_for_question_active


def set_is_tweet_for_question_active(is_active):
    global is_tweet_for_question_active
    is_tweet_for_question_active = is_active


