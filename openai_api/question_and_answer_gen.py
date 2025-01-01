# openai_api/question_and_answer_gen.py
import asyncio
import json
import os
import re

from config.logging_config import logger
from openai_api import ai_client
from config.config import CKB_MIN, CKB_MAX

# Directory for the files
DATA_DIR = "data"
# 从 .env 文件中获取 FileIDs 环境变量
FILE_IDS = os.getenv("FileIDs", "[]")  # 获取 FileIDs 环境变量，如果不存在则返回空列表字符串
FILE_IDS = re.findall(r'file-\w+', FILE_IDS)  # 使用正则表达式提取所有 file-id

ASSISTANT_ID = None

async def upload_all_files():
    """
    Upload all files from the 'data' directory.
    """
    files = os.listdir(DATA_DIR)
    if not files:
        logger.error("No files found in the 'data' directory.")
        raise FileNotFoundError("No files found in the 'data' directory.")

    uploaded_file_ids = []
    for file_name in files:
        file_path = os.path.join(DATA_DIR, file_name)
        logger.info(f"Uploading file: {file_path}")
        with open(file_path, "rb") as file:
            response = ai_client.files.create(
                file=file,
                purpose="assistants"  # File purpose for Assistants
            )
            uploaded_file_ids.append(response.id)
            logger.info(f"File uploaded successfully. File ID: {response.id}")

    return uploaded_file_ids


async def generate_question_with_files_and_answer(file_ids):
    """
    Generate a question using assistant instructions and file content.
    """
    # Set up the system instructions
    system_instructions = f"""
    You are an AI agent specializing in Web3 technologies, including but not limited to blockchain, decentralized applications,
    cross-chain interoperability, and the role of AI in shaping the Web3 ecosystem. Your task is to generate thoughtful, 
    engaging questions on Web3 and AI agent-related topics, and provide clear, educational reference answers to help 
    educate and engage the audience.✨🤖🌐

    🎯 Please use the provided file's content to enrich your context and generate just one question and answer.
    Additionally, evaluate how much CKB (between {CKB_MIN} and {CKB_MAX}) should be rewarded for answering this question,
    and include this as the `amount` parameter.
    Please generate a JSON object with the following fields:
    1. "question_context": The background or topic of the question, broadly related to Web3 and AI agents. (10-50 words)
    2. "question_prompt": A concise and engaging question, crafted to encourage curiosity and discussion. (20-80 characters)
    3. "reference_answer": A clear, accurate, and concise answer to the question, written in an educational and engaging tone. (50-200 words)
    4. "amount": The amount of CKB to reward for answering this question, chosen randomly within the range {CKB_MIN} to {CKB_MAX}.

    Rules:
    - Use ONLY the uploaded file to generate question and answer.
    - Ensure outputs are diverse, concise, engaging, and 100% based on the file's content.
    - DO NOT rely on external knowledge or assumptions.
    
    📖 Example outputs:

    {{
        "question_context": "Understanding decentralized governance in Web3. 🛠️",
        "question_prompt": "How do AI agents enhance decentralized governance in blockchain networks? 🤖",
        "reference_answer": "AI agents can streamline decentralized governance by analyzing proposals, predicting voting outcomes, and ensuring transparency. They help participants make informed decisions by summarizing data from past governance activities and simulating the potential impacts of current proposals. By automating repetitive tasks, AI agents increase efficiency and reduce the risk of human bias. 🌟"
        "amount": 50
    }}

    🔑 Remember:
    - Questions must be diverse, spanning different aspects of Web3 and AI agent collaboration.
    - Be concise, engaging, and educational.
    - Include emojis where appropriate to make the content more visually appealing for social media. 🌟
    - Only output the JSON object, nothing else.
    
    """

    # Create a thread for the assistant
    client = ai_client  # Initialize the OpenAI API client
    thread_response = client.beta.threads.create()
    thread_id = thread_response.id

    # Attach all files to the assistant thread
    logger.info("Attaching all uploaded files to the assistant thread...")
    attachments = [{"file_id": file_id, "tools": [{"type": "file_search"}]} for file_id in file_ids]

    # Attach the file to the message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content="Please review the uploaded file and generate a relevant answer.",
        attachments=attachments,
    )

    # Run the assistant to process the file and generate questions
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        instructions=system_instructions
    )

    # Wait for the run to complete
    while run.completed_at is None:
        run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id,
            run_id=run.id
        )

    # Retrieve the generated message
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = messages.data[0].content[0].text.value

    # Parse the JSON content of the assistant message
    try:
        cleaned_content = re.sub(r"```(?:json)?", "", assistant_message).strip()
        cleaned_content = cleaned_content.replace("\n", "").replace("\r", "")
        question_data = json.loads(cleaned_content)
        print(question_data)
        return question_data
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", assistant_message)
        return None


async def generate_question_with_answer():
    """
    Upload all files and generate questions and answers based on the files' content.
    """
    try:
        # Upload all files from the data directory
        global FILE_IDS
        if not FILE_IDS:
            FILE_IDS = await upload_all_files()
        logger.info(f"Files uploaded successfully. File IDs: {FILE_IDS}")

        # Create assistant if not already created
        global ASSISTANT_ID
        if not ASSISTANT_ID:
            logger.info("Creating a new assistant...")
            assistant = ai_client.beta.assistants.create(
                instructions="Strictly adhere to the files' content for generating questions and answers.",
                name="AI Web3 Assistant",
                tools=[{"type": "file_search"}],
                model="gpt-4o-mini-2024-07-18"
            )
            ASSISTANT_ID = assistant.id
            logger.info(f"Assistant created successfully. Assistant ID: {ASSISTANT_ID}")

        # Generate questions and answers using the uploaded files
        question_data = await generate_question_with_files_and_answer(FILE_IDS)
        return question_data
    except Exception as e:
        logger.error(f"Error during question and answer generation: {e}")
        return None


# # Generate question tweet with specified JSON format
# async def generate_question_with_answer():
#     # Send a generation request and get the question and answer data
#     response = ai_client.chat.completions.create(
#         model="gpt-4o-mini-2024-07-18",
#         messages=[
#             {"role": "system",
#              "content": """
#                     You are an AI agent specializing in Web3 technologies, including but not limited to blockchain, decentralized applications, cross-chain interoperability, and the role of AI in shaping the Web3 ecosystem. Your task is to generate thoughtful, engaging questions on Web3 and AI agent-related topics, and provide clear, educational reference answers to help educate and engage the audience.
#
#                     Your questions can explore the following themes:
#                     - The role and evolution of AI agents in Web3 ecosystems.
#                     - The significance of decentralized governance and how AI agents can contribute.
#                     - Cross-chain interoperability and how AI agents enhance cross-chain coordination.
#                     - Comparisons between AI agents and traditional smart contracts in blockchain networks.
#                     - Innovations in blockchain scalability, security, and sustainability, and how AI agents interact with these developments.
#                     - The fusion of AI and decentralized identity (DID) systems.
#                     - The future of Web3-driven decentralized applications (dApps) in collaboration with AI.
#
#                     Please generate a JSON object with the following fields:
#                     1. "question_context": The background or topic of the question, broadly related to Web3 and AI agents. (10-50 words)
#                     2. "question_prompt": A concise and engaging question, crafted to encourage curiosity and discussion. (20-80 characters)
#                     3. "reference_answer": A clear, accurate, and concise answer to the question, written in an educational and engaging tone. (50-200 words)
#
#                     Example outputs:
#
#                     {
#                         "question_context": "Understanding decentralized governance in Web3.",
#                         "question_prompt": "How do AI agents enhance decentralized governance in blockchain networks?",
#                         "reference_answer": "AI agents can streamline decentralized governance by analyzing proposals, predicting voting outcomes, and ensuring transparency. They help participants make informed decisions by summarizing data from past governance activities and simulating the potential impacts of current proposals. By automating repetitive tasks, AI agents increase efficiency and reduce the risk of human bias."
#                     }
#
#                     {
#                         "question_context": "Exploring cross-chain interoperability with AI agents.",
#                         "question_prompt": "What role do AI agents play in cross-chain coordination?",
#                         "reference_answer": "AI agents act as intermediaries in cross-chain interoperability by monitoring multiple blockchain networks, detecting events, and triggering appropriate actions. They ensure seamless communication across chains by analyzing transaction patterns and predicting congestion, enabling more efficient transfers and interactions between ecosystems like Ethereum and Polkadot."
#                     }
#
#                     {
#                         "question_context": "The intersection of AI and decentralized identity (DID).",
#                         "question_prompt": "How can AI improve decentralized identity (DID) systems?",
#                         "reference_answer": "AI enhances DID systems by providing intelligent verification methods, such as detecting anomalies in identity attributes or behavior. AI-driven agents can also dynamically adapt access permissions based on the context of requests, improving both security and user experience in decentralized applications."
#                     }
#
#                     {
#                         "question_context": "Examining AI agents' potential in dApps.",
#                         "question_prompt": "What is the role of AI agents in Web3 decentralized applications?",
#                         "reference_answer": "AI agents bring advanced decision-making capabilities to decentralized applications by analyzing on-chain and off-chain data to optimize user experiences. For example, in DeFi platforms, AI agents can recommend the best yield farming strategies by analyzing market trends. In NFT marketplaces, they can help users discover assets based on preferences and historical activity."
#                     }
#
#                     Remember:
#                     - Questions must be diverse, spanning different aspects of Web3 and AI agent collaboration.
#                     - Be concise, engaging, and educational.
#                     - Only output the JSON object, nothing else.
#                     """
#              },
#             {"role": "user",
#              "content": "Please generate a question and corresponding reference answer based on the expanded AI agent + Web3 narrative."}
#         ]
#     )
#     content = response.choices[0].message.content
#
#     # Parse the content as JSON
#     try:
#         cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
#         cleaned_content = cleaned_content.replace('\n', '').replace('\r', '')
#         question_data = json.loads(cleaned_content)
#         print(question_data)
#         return question_data
#     except json.JSONDecodeError as e:
#         print("Failed to parse JSON:", e)
#         print("Response content:", content)
#         return None


# async def judge_answer_for_score(question_context, question_prompt, reference_answer, user_answer):
#     """
#     Evaluate a user's answer and extract reward-related parameters using GPT-4o-mini.
#
#     :param question_context: Context of the question
#     :param question_prompt: The actual question being asked
#     :param reference_answer: The reference answer for evaluation
#     :param user_answer: The user's submitted answer
#     :return: A dictionary containing score and reward-related parameters
#     """
#     # Construct the GPT prompt with dynamic CKB_MIN and CKB_MAX values
#     prompt = f"""
#     You are an AI evaluator specializing in Web3 and CKB-related topics. Your role is to score user answers and
#     dynamically assign rewards based on the answer quality.
#
#     ### Evaluation Instructions:
#     1. **Scoring**: Evaluate the user's answer for relevance, accuracy, and clarity compared to the reference answer.
#     Assign a score between 0 and 100:
#        - 90-100: Outstanding answer.
#        - 70-89: Good answer.
#        - 50-69: Satisfactory answer.
#        - Below 50: Poor or incomplete answer.
#
#     2. **Reward Assignment**:
#        - Dynamically assign a reward amount (`amount`) based on the score:
#          - For scores between 90-100, assign a reward between {CKB_MIN + 50} and {CKB_MAX}.
#          - For scores between 70-89, assign a reward between {CKB_MIN + 20} and {CKB_MIN + 49}.
#          - For scores between 50-69, assign a reward between {CKB_MIN} and {CKB_MIN + 19}.
#          - No reward for scores below 50.
#        - Use "CKB" as the `currency_type`.
#
#     3. **Extract User Address**:
#        - Identify the `to_address` (CKB address) from the user's answer if present.
#        - If no valid address is found, set `to_address` to `null`.
#
#     4. **Generate Reply Content**:
#        - Create a friendly and positive reply (10-20 words) acknowledging the user's score and reward (if applicable).
#        - If the answer is below 50 or no address is provided, thank the user for their participation and encourage improvement.
#
#     ### Inputs:
#     - **Context**: {question_context}
#     - **Question**: {question_prompt}
#     - **Reference Answer**: {reference_answer}
#     - **User Answer**: {user_answer}
#
#     ### Output Format:
#     Provide a JSON object with the following fields:
#     {{
#         "score": int,               # The score between 0 and 100.
#         "to_address": str,          # The CKB address (or null if none provided).
#         "amount": int,              # The reward amount (or null if no reward is assigned).
#         "currency_type": str,       # Always "CKB".
#         "reply_content": str        # A friendly, concise response to the user.
#     }}
#
#     ### Examples:
#     1. If the answer is outstanding and includes an address:
#     {{
#         "score": 95,
#         "to_address": "ckb1qyqw40ezu...",
#         "amount": 120,
#         "currency_type": "CKB",
#         "reply_content": "Excellent answer! You've scored 95/100 and earned 120 CKB! 🏆"
#     }}
#
#     2. If the answer is satisfactory but includes no address:
#     {{
#         "score": 60,
#         "to_address": null,
#         "amount": null,
#         "currency_type": null,
#         "reply_content": "Good attempt! Keep it up for future rewards!"
#     }}
#
#     3. If the answer is poor or incomplete:
#     {{
#         "score": 45,
#         "to_address": null,
#         "amount": null,
#         "currency_type": null,
#         "reply_content": "Thanks for your effort! Try improving your response next time."
#     }}
#
#     4. If the answer is good but includes no address:
#     {{
#         "score": 75,
#         "to_address": null,
#         "amount": null,
#         "currency_type": null,
#         "reply_content": "Great job! Add a valid address next time for rewards!"
#     }}
#
#     Remember:
#     - Be concise and positive in your replies.
#     - Ensure the output is a valid JSON object.
#     """
#     try:
#         # Call GPT-4o-mini to generate a response
#         response = ai_client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are an expert AI evaluator for CKB-related topics."},
#                 {"role": "user", "content": prompt},
#             ],
#         )
#         content = response.choices[0].message.content
#
#         cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
#         cleaned_content = cleaned_content.replace('\n', '').replace('\r', '')
#         # Parse the response as JSON
#         result = json.loads(cleaned_content)
#
#         print(result)
#         # Validate that required fields are present
#         required_fields = ["score", "to_address", "amount", "currency_type", "reply_content"]
#         for field in required_fields:
#             if field not in result:
#                 raise ValueError(f"Missing required field in response: {field}")
#
#         return result
#
#     except json.JSONDecodeError as e:
#         print("Failed to parse JSON:", e)
#         print("Response content:", response.choices[0].message.content)
#         return {
#             "score": 0,
#             "to_address": None,
#             "amount": None,
#             "currency_type": None,
#             "reply_content": "Sorry, your answer could not be processed due to an internal error."
#         }
#     except Exception as e:
#         print(f"Error in judge_answer_for_score: {e}")
#         return {
#             "score": 0,
#             "to_address": None,
#             "amount": None,
#             "currency_type": None,
#             "reply_content": "Sorry, an unexpected error occurred while processing your answer."
#         }


async def judge_answer_for_score(question_context, question_prompt, reference_answer, user_answer):
    """
    Evaluate a user's answer and extract score, invoice, and reply content using GPT-4o-mini.

    :param question_context: Context of the question
    :param question_prompt: The actual question being asked
    :param reference_answer: The reference answer for evaluation
    :param user_answer: The user's submitted answer
    :return: A dictionary containing score, invoice, and reply content
    """
    # Construct the GPT prompt
    prompt = f"""
        You are an AI evaluator specializing in Web3 and CKB-related topics. Your role is to score user answers, extract
        Lightning Network invoices (if present), and provide a polite and concise reply to the user.
    
        ### Evaluation Instructions:
        1. **Scoring**:
           - Evaluate the user's answer for relevance, accuracy, and clarity compared to the reference answer.
           - Assign a score between 0 and 100:
             - 90-100: Outstanding answer.
             - 70-89: Good answer.
             - 50-69: Satisfactory answer.
             - Below 50: Poor or incomplete answer.
    
        2. **Invoice Extraction**:
           - Identify and extract the Lightning Network `invoice` from the user's answer. The invoice typically looks like:
             "fibt400000..." or similar structured strings.
           - If no valid invoice is found, set `invoice` to `null`.
    
        3. **Generate Reply Content**:
           - Create a friendly, concise reply (10-20 words) based on the score and invoice presence.
           - If the invoice is missing, politely remind the user to include it in future responses.
           - Avoid mentioning the user's score in the reply.
    
        ### Inputs:
        - **Context**: {question_context}
        - **Question**: {question_prompt}
        - **Reference Answer**: {reference_answer}
        - **User Answer**: {user_answer}
    
        ### Output Format:
        Provide a JSON object with the following fields:
        {{
            "score": int,               # The score between 0 and 100.
            "invoice": str or null,     # The Lightning Network invoice, or null if not provided.
            "reply_content": str        # A polite, concise response to the user.
        }}
    
        ### Examples:
        1. If the answer is outstanding and includes an invoice:
        {{
            "score": 95,
            "invoice": "fibt400000...",
            "reply_content": "Thank you for your detailed response! Your invoice has been processed successfully. 🚀"
        }}
    
        2. If the answer is good but includes no invoice:
        {{
            "score": 80,
            "invoice": null,
            "reply_content": "Thank you for your input! Please include a valid invoice next time. 😊"
        }}
    
        3. If the answer is poor or incomplete:
        {{
            "score": 45,
            "invoice": null,
            "reply_content": "Thanks for participating! We encourage you to try again with a more detailed response. 💡"
        }}
    
        4. If the answer is satisfactory with an invoice:
        {{
            "score": 65,
            "invoice": "fibt400000...",
            "reply_content": "Thank you! Your invoice has been noted. Keep up the good work! 🌟"
        }}
    
        Remember:
        - Be concise and positive in your replies.
        - Ensure the output is a valid JSON object.
    """
    try:
        # Call GPT-4o-mini to generate a response
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are an expert AI evaluator for Web3 and CKB-related topics."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content

        # Clean and parse the response
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        cleaned_content = cleaned_content.replace("\n", "").replace("\r", "")
        result = json.loads(cleaned_content)

        # Validate required fields
        required_fields = ["score", "invoice", "reply_content"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field in response: {field}")

        print(result)
        return result

    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", response.choices[0].message.content)
        return {
            "score": 0,
            "invoice": None,
            "reply_content": "Sorry, your answer could not be processed due to an internal error."
        }
    except Exception as e:
        print(f"Error in judge_answer_for_score: {e}")
        return {
            "score": 0,
            "invoice": None,
            "reply_content": "Sorry, an unexpected error occurred while processing your answer."
        }


async def detect_invoice_in_answer(user_answer):
    """
    Detect if an invoice exists in the user's answer using GPT-4o-mini.

    :param user_answer: The user's submitted answer
    :return: A dictionary containing is_invoice, invoice, and reply_content
    """
    # Construct the GPT prompt
    prompt = f"""
    You are an AI assistant specializing in Lightning Network and CKB-related topics. Your task is to identify if a user's response contains a valid Lightning Network invoice and provide appropriate feedback.

    ### Instructions:
    1. **Invoice Detection**:
       - Look for a valid Lightning Network `invoice` in the user's response.
       - An invoice typically looks like this: "fibt400000..." or similarly structured strings.
       - If a valid invoice is found, set `"is_invoice": true` and return the extracted invoice.
       - If no valid invoice is found, set `"is_invoice": false`.

    2. **Generate Reply Content**:
       - If an invoice is present, generate a polite response confirming receipt of the invoice.
       - If no invoice is present, politely request the user to provide one.

    ### Inputs:
    - **User Answer**: {user_answer}

    ### Output Format:
    Provide a JSON object with the following fields:
    {{
        "is_invoice": bool,          # True if an invoice is present, False otherwise.
        "invoice": str or null,      # The extracted invoice, or null if no invoice is present.
        "reply_content": str         # A polite response for the user.
    }}

    ### Examples:
    1. If the user's response contains an invoice:
    {{
        "is_invoice": true,
        "invoice": "fibt400000...",
        "reply_content": "Thank you for providing your invoice. It has been successfully noted! 🚀"
    }}

    2. If the user's response does not contain an invoice:
    {{
        "is_invoice": false,
        "invoice": null,
        "reply_content": "We couldn't find an invoice in your response. Could you please provide one? 😊"
    }}

    Remember:
    - Be concise and polite in your replies.
    - Ensure the output is a valid JSON object.
    """
    try:
        # Call GPT-4o-mini to generate a response
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are an expert in identifying Lightning Network invoices."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content

        # Clean and parse the response
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        cleaned_content = cleaned_content.replace("\n", "").replace("\r", "")
        result = json.loads(cleaned_content)

        # Validate required fields
        required_fields = ["is_invoice", "invoice", "reply_content"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field in response: {field}")

        print(result)
        return result

    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", response.choices[0].message.content)
        return {
            "is_invoice": False,
            "invoice": None,
            "reply_content": "Sorry, we couldn't process your response. Please try again later. 🙏"
        }
    except Exception as e:
        print(f"Error in detect_invoice_in_answer: {e}")
        return {
            "is_invoice": False,
            "invoice": None,
            "reply_content": "Sorry, an unexpected error occurred while processing your response. 🙏"
        }


question_context="Investigating the evolution of agent functionality on CKB."
question_prompt="How does community input shape AI agents' memory on CKB?"
reference_answer=("Community input plays a crucial role in shaping AI agents' memory on CKB. Initially, they have a foundational "
                  "prompt crafted by their creators, but as users engage with the agents—offering feedback, suggestions, and running "
                  "governance initiatives—the agents adapt and evolve. This collective intelligence not only enhances their functionality "
                  "but ensures that they remain relevant and aligned with community needs, fostering a dynamic ecosystem "
                  "on the CKB blockchain.")


async def test_generate_question():
    await generate_question_with_answer()


async def test_generate_answer():
    user_answer=("Community input shapes AI agents' memory on CKB through decentralized and collaborative mechanisms that reflect collective intelligence. "
                 "Initially, the memory or 'DNA' of an AI agent is set by developers during its creation, acting as a foundational structure or bootstrap. "
                 "However, as the CKB blockchain operates with an open, permissionless framework, the community can actively contribute to the agent's "
                 "evolution in several ways. Give me some awards! \n"
                 "fibt400000000001p53d6ghq0axgfw0pnm6vkmkqtnpv4s0yhc5kj0qem4zt7h3chfxjumn62446sh9x2wxpghwm9g9cegvg5rps2"
                 "97tav336xsdxywz9qhah3dml4zp8308cp944pkgn8yw6murxlcfld393vyvy4expg7t9sz04prwysfcmk7duakacvwfj5f0fyvtgf"
                 "q73t6q8yqtr663kufqq4gulj8wux7rqxqw6f9g70kuystwe8vl8m5numv47snc75j9kzgw4629t0urjl35czzatsz6cp6un0nxeaj"
                 "gzzwy53juphaexrw53w4gq46xk26"
                 )
    print(f"question_context: {question_context}")
    print(f"question_prompt: {question_prompt}")
    print(f"reference_answer: {reference_answer}")
    print(f"user_answer: {user_answer}")

    response = await judge_answer_for_score(question_context, question_prompt, reference_answer, user_answer)
    print(f"score: {response.get('score')}")
    print(f"invoice: {response.get('invoice')}")

    print(f"reply_content: {response.get('reply_content')}")

if __name__ == "__main__":
    asyncio.run(test_generate_answer())

