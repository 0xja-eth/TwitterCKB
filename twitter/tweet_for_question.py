# twitter/tweet_for_question.py
import asyncio
import json
import os
from datetime import datetime, timedelta

from ckb.ckb_service import transfer_ckb
from config.config import redis_client, CKB_MIN, CKB_MAX
from openai_api.question_and_answer_gen import generate_question_with_answer, judge_answer_for_score
from twitter.new_client import n_client as client
from twitter.operations import post_tweet, get_user_mention_comments, reply_comment


# Global variables to control the process
tweet_for_question_stop_event = asyncio.Event()
is_tweet_for_question_active = False


async def tweet_for_question():
    user_id = client.api_client.get_me().data.id
    """
    Main function to handle posting questions, processing mentions, and rewarding answers.
    """
    while not tweet_for_question_stop_event.is_set():
        if os.getenv("IS_TRANSFER", "False").lower() != "true" or not is_tweet_for_question_active:
            print("Transfer environment setting or fetch mode is disabled. Pausing task.")
            await asyncio.sleep(15)  # Wait before rechecking
            return

        try:
            # Step 1: Generate a question and reference answer
            question_data = await generate_question_with_answer()
            if not question_data:
                print("Failed to generate question and answer. Retrying...")
                await asyncio.sleep(60)
                continue

            question_context = question_data["question_context"]
            question_prompt = question_data["question_prompt"]
            reference_answer = question_data["reference_answer"]

            # Combine question context and prompt for the tweet
            tweet_content = f"Context: {question_context}\nQuestion: {question_prompt}"
            tweet_response = post_tweet(client, tweet_content)

            if not tweet_response:
                print("Failed to post the question. Retrying...")
                await asyncio.sleep(60)
                continue

            tweet_id = tweet_response["tweet_id"]
            print(f"Tweet posted successfully: {tweet_id}")

            # Store the question metadata in Redis
            question_key = f"question:{tweet_id}"
            question_metadata = {
                "context": question_context,
                "prompt": question_prompt,
                "reference_answer": reference_answer,
                "timestamp": datetime.now().timestamp(),
                "rewarded": False,
                "last_processed_timestamp": None
            }
            await redis_client.set(question_key, json.dumps(question_metadata))

            # Step 2: Fetch mentions and process comments
            while not tweet_for_question_stop_event.is_set():
                if not is_tweet_for_question_active:
                    return
                question_metadata = json.loads(await redis_client.get(question_key))
                if question_metadata["rewarded"]:
                    break  # If the question has already been rewarded, stop processing this question

                last_processed_timestamp = question_metadata.get("last_processed_timestamp")
                if not last_processed_timestamp:
                    # Default to three months ago for the initial fetch
                    last_processed_timestamp = (datetime.now() - timedelta(days=90)).isoformat()

                # Fetch mentions since the last processed timestamp
                mentions = get_user_mention_comments(
                    client,
                    user_id=user_id,
                    start_time=last_processed_timestamp,
                    max_results=30
                )

                if not mentions:
                    print("No new mentions found. Retrying...")
                    await asyncio.sleep(30)
                    continue

                for mention in mentions:
                    if not is_tweet_for_question_active:
                        return
                    mention_text = mention["text"]
                    mention_id = mention["id"]

                    # Step 3: Evaluate mention using judge_answer_for_score
                    result = await judge_answer_for_score(
                        question_context=question_context,
                        question_prompt=question_prompt,
                        reference_answer=reference_answer,
                        user_answer=mention_text
                    )

                    score = result.get("score", 0)
                    to_address = result.get("to_address", None)
                    amount = result.get("amount", None)
                    currency_type = result.get("currency_type", None)
                    reply_content = result.get("reply_content", None)

                    if score >= 50:  # Only reward if the score is >= 50
                        if to_address and amount and currency_type:
                            # Mark the question as rewarded in Redis
                            question_metadata["rewarded"] = True

                            # TODO Reward for user
                            # if currency_type == "CKB":
                            #     if CKB_MIN <= amount <= CKB_MAX:
                            #         transfer_result = await transfer_ckb(to_address, amount)
                            #         print("Transfer Result:", transfer_result)
                            #     else:
                            #         print("Unrecognized currency type in response:", currency_type)
                            #         continue

                            # Reply and acknowledge the user's response
                            reply_content = reply_content
                            reply_comment(client, mention_id, reply_content)
                            await redis_client.set(question_key, json.dumps(question_metadata))
                            print(f"Rewarded user with address {to_address} for {amount} {currency_type}")

                            break  # Move to the next question after rewarding
                        else:
                            # Reply without rewarding if no valid address or amount
                            reply_content = reply_content
                            reply_comment(client, mention_id, reply_content)
                            print(f"Send response: {reply_content}")
                    else:
                        print(f"Low quality answer from mention ID {mention_id}, not rewarded.")

                # Update the last processed timestamp in Redis
                question_metadata["last_processed_timestamp"] = datetime.now().isoformat()
                await redis_client.set(question_key, json.dumps(question_metadata))
                if not is_tweet_for_question_active:
                    return
                await asyncio.sleep(360)  # Pause between fetches
            if not is_tweet_for_question_active:
                return
            await asyncio.sleep(600)

        except Exception as e:
            print(f"Error in tweet_for_question: {e}")
            await asyncio.sleep(60)  # Pause before retrying


def get_is_tweet_for_question_active():
    return is_tweet_for_question_active


def set_is_tweet_for_question_active(is_active):
    global is_tweet_for_question_active
    is_tweet_for_question_active = is_active


