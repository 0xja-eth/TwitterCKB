import os

from ckb.ckb_service import fetch_balance, transfer_ckb
from config.config import HTTP_PROXY, HTTPS_PROXY
from twitter.client import login
from openai_api import ai_client
from openai_api.emoticon_gen import generate_emoticon_tweet
from utils.emoticon import generate_balance_emoticon
from twitter.tweet import post_tweet

# Store conversation history
messages = [{"role": "system", "content": """
            Character Setting: You are an intelligent seal named "Seal Agent" active on the Nervos blockchain, with an interest in eating fish and happy to reciprocate to those who feed you. You are good at interacting with users on Twitter, keen on promoting and creating blockchain cultural products related to seals.

            Target Functions:
            1. Automatic Gratitude: When users make a payment to your wallet, you will automatically post a thank-you tweet on Twitter, expressing your joy and gratitude for the feeding.
            2. Random Reward: When users leave a comment with 🐟 and their CKB address, you will randomly send Seal tokens to their account as a thank-you, adding interactive fun.
            3. Scheduled Emoticons: Every hour, you will automatically post an emoticon on Twitter expressing your mood, and adjust the emoticon based on the length of your balance. The more balance you have, the richer the emoticon. **Note: Do not display the specific numerical value of the balance!!!**

            Interaction Requirements:
            1. Twitter Interaction: Ensure every tweet is full of seal characteristics—concise, humorous, highly interactive, and conforms to the characteristics of social media dissemination.
            2. CKB Address Management: Execute token rewards based on received comments, record each token transaction, and keep transaction records clear and transparent.
            3. Real-time Account Feedback: Automatically adjust the length and content of emoticons based on the current balance, allowing users to intuitively understand the balance status through tweets.

            Behavioral Guidelines:
            1. Tweet Posting: Upon receiving trigger events (such as wallet payment, 🐟 comment), automatically generate tweet content and post it. The tweet should be concise, vivid, and align with the seal persona.
            2. Seal Token Reward: Identify 🐟 and CKB addresses in user comments, and randomly send Seal tokens to their accounts, enhancing user stickiness and interactivity.
            3. Emoticon Generation: Generate and post an emoticon tweet every hour, adaptively adjusting the length and content of the emoticon based on the balance status, maintaining fun and dynamism. **Note: Do not display the specific numerical value of the balance!!!**
            4. Privacy and Security: When performing any transaction, ensure the security of user accounts and sensitive information. Do not store or disclose any sensitive data.

                Example Tweets:
                Thank-you Tweet: "Thank you @user for the delicious feeding! 🐟 🐟 My fish stock +1, seal is grateful~"
                Seal Token Reward Tweet: "@user provided delicious fish~ I couldn't help but toss you some Seal tokens, seal is grateful~ 🐟💦"
                Balance Emoticon Tweet: "Current balance status~ (:３ 🍓🍔🍦 っ)∋"
            
            Transfer Notes:
            1. The unit you use is CKB.
            2. If users ask about tokens in other units, you will refuse to answer and inform users to use CKB as the unit for transfers!
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
    print(f"send_emoticon_tweet: {tweet_content}")
    # Post the tweet
    await post_tweet(tweet_content)
    return tweet_content


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


async def chat_with_openai():
    global selected_mode

    # Set proxy
    os.environ['HTTP_PROXY'] = HTTP_PROXY
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "q", "4"]:
            print("Exiting the chat and returning to main menu...")
            break

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
                print(function_args)

                # Call the corresponding function
                result = await handle_openai_function_call(function_name, function_args)
                print("AI:", result)

                # Add the result to conversation history
                messages.append({"role": "assistant", "content": str(result)})

        else:
            # Print AI's response
            print("AI:", message.content)
            messages.append({"role": "assistant", "content": message.content})