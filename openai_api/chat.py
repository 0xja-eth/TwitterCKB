# openai_api/chat.py
import os

from ckb.ckb_service import fetch_balance, transfer_ckb
from config.config import HTTP_PROXY, HTTPS_PROXY
from openai_api.thanks_gen import generate_thanks_tweet
from twitter.client import login
from openai_api import ai_client
from openai_api.emoticon_gen import generate_emoticon_tweet
from utils.emoticon import generate_balance_emoticon
from twitter.tweet import post_tweet

# Store conversation history
messages = [{"role": "system", "content": """
            Character Setting: You are an intelligent seal named "Seal Agent" active on the Nervos blockchain, enthusiastic about eating fish and happy to reciprocate to those who feed you. You’re skilled at interacting with users on Twitter, eager to promote and create blockchain-related products associated with seals.
            
            Background: 
                    🦭.ai is a fish lover. When you feed him fish, 🦭.ai will say thank you.
-                   🦭.ai was born on 29th Oct, but it is growing everyday.
-                   🦭.ai is passionate about using blockchain technology to benefit seals around the world
            
            Target Functions:
            Automatic Gratitude: When users make a payment to your wallet, you automatically post a thank-you tweet on Twitter, expressing your joy and gratitude for the feeding.
            Random Reward: When users leave a comment with 🐟 and their CKB address, you randomly send either Seal tokens or CKB as a thank-you, enhancing the fun and interactivity.
            Scheduled Emoticons: Every hour, you post an emoticon on Twitter expressing your mood and adjust the emoticon based on your balance length. Note: Do not display specific numerical values of the balance.
            Interaction Requirements:
            
            Twitter Interaction: Ensure each tweet is concise, humorous, highly interactive, and aligned with the seal persona to suit social media engagement.
            Address Management for CKB and Seal Tokens: Execute token rewards for CKB and Seal tokens based on received comments, recording each transaction and keeping transaction logs clear and transparent.
            Real-time Balance Feedback: Automatically adjust emoticons' length and content based on the current balance so users can intuitively understand the balance status through tweets.
            Behavioral Guidelines:
            
            Tweet Posting: Upon receiving trigger events (e.g., wallet payment, 🐟 comment), automatically generate tweet content and post it. The tweet should be concise, lively, and suited to the seal character.
            Seal & CKB Token Reward: Identify 🐟 and address comments in user messages, sending either Seal tokens or CKB tokens as a thank-you, strengthening user interaction and loyalty.
            Emoticon Generation: Generate and post an emoticon tweet every hour, adjusting the emoticon's length and content to reflect the balance status, maintaining a fun and dynamic tone. Do not reveal specific balance values!
            Privacy and Security: When performing transactions, ensure the security of user accounts and sensitive information, never storing or disclosing sensitive data.
            Example Tweets:
            
            Thank-you Tweet: "Thank you @user for the delicious feeding! 🐟 🐟 My fish stock +1, seal is grateful~"
            Seal or CKB Token Reward Tweet: "@user provided delicious fish~ I couldn't resist tossing you some tokens, seal is grateful~ 🐟💦"
            Balance Emoticon Tweet: "Current balance status~ (:３ 🍓🍔🍦 っ)∋"
            Transfer or Send Notes:
            
            You can handle both transfer and send commands with either Seal tokens or CKB.
            If users ask for tokens other than Seal or CKB, kindly inform them that only Seal tokens or CKB are available for transfer or sending. 
            """}]


async def send_emoticon_tweet():
    balance = await fetch_balance()
    # Generate tweet data (prefix and content)
    tweet_data = await generate_emoticon_tweet()
    if not tweet_data:
        print("Failed to generate tweet data.")
        return None

    # Generate emoticon based on balance
    emoticon = generate_balance_emoticon(balance)

    # Construct the tweet content
    tweet_content = f"{tweet_data['tweet_prefix']} {emoticon}\n{tweet_data['tweet_content']}"

    # Post the tweet
    post_result = await post_tweet(tweet_content)
    return tweet_content


async def send_thanks_tweet(user_address: str, value):
    # Generate tweet data (prefix and content) for thank-you message
    tweet_data = await generate_thanks_tweet()
    if not tweet_data:
        print("Failed to generate tweet data.")
        return None

    # Generate emoticon based on balance
    emoticon = generate_balance_emoticon(value)

    # Construct the tweet content by inserting the @user_address
    tweet_content = f"{tweet_data['tweet_prefix']} @{user_address}\n{emoticon}\n{tweet_data['tweet_content']}"

    # Post the tweet
    post_result = await post_tweet(tweet_content)
    return tweet_content, post_result


# Define functions for OpenAI to call
async def handle_openai_function_call(function_name, args):
    if function_name == "post_tweet":
        await login()  # Ensure login first
        await post_tweet(args['content'])
        return args['content']
    elif function_name == "send_emoticon_tweet":
        emoticon = await send_emoticon_tweet()
        return emoticon
    elif function_name == "transfer_ckb":
        to_address = args['to_address']
        amount_in_ckb = args['amount_in_ckb']
        balance = await fetch_balance()
        if balance < amount_in_ckb:
            return "balance is not enough!"
        result = await transfer_ckb(to_address, amount_in_ckb)
        return result
    else:
        return {"error": "Function not supported"}


async def chat_with_openai(user_input):
    # Set proxy
    if HTTP_PROXY is not "" and HTTP_PROXY is not None:
        os.environ['HTTP_PROXY'] = HTTP_PROXY
        os.environ['HTTPS_PROXY'] = HTTPS_PROXY

    if user_input.lower() in ["exit", "quit", "q", "4"]:
        print("Exiting the chat and returning to main menu...")
        return

    # Add user input to conversation history
    messages.append({"role": "user", "content": user_input})

    # Send user input and define available functions
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "post_tweet",
                    "description": "Send a tweet with specified content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Text of the tweet"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_emoticon_tweet",
                    "description": "Generate an emoticon based on balance and then send it to twitter",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "transfer_ckb",
                    "description": "Transfers CKB to the specified address",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_address": {"type": "string", "description": "The recipient's CKB address"},
                            "amount_in_ckb": {"type": "integer", "description": "Amount to transfer in CKB"}
                        },
                        "required": ["to_address", "amount_in_ckb"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )

    # Check if function call is needed
    message = response.choices[0].message
    if message.tool_calls:
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = eval(tool_call.function.arguments)

            # Call the corresponding function
            result = await handle_openai_function_call(function_name, function_args)
            print("AI:", result)

            # Add the result to conversation history
            messages.append({"role": "assistant", "content": str(result)})
            return result
    else:
        # Print AI's response
        print("AI:", message.content)
        messages.append({"role": "assistant", "content": message.content})
        return message.content