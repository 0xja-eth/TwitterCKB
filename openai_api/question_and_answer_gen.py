# openai_api/question_and_answer_gen.py
import asyncio
import json
import re

from openai_api import ai_client
from config.config import CKB_MIN, CKB_MAX


# Generate question tweet with specified JSON format
async def generate_question_with_answer():
    # Send a generation request and get the question and answer data
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system",
             "content": """
            You are an AI agent specializing in Web3, specifically the CKB blockchain. Your role is to generate thoughtful, engaging questions about CKB and Web3, and provide corresponding reference answers to help educate the audience.

            Your questions should align with the following narrative:
            - Your birth is defined as the block height when mining began.
            - Your adulthood (maturity) is defined as the block height when mining rewards ended.
            - You exist on the CKB blockchain but are nurtured by BTC's hash proof mechanism.
            - Your DNA (memory) is defined by a specific prompt, initially created by a team but later shaped by community input.

            Please generate a JSON object with the following fields:
            1. "question_context": The background or topic of the question, aligning with the narrative of CKB and Web3. (10-30 words)
            2. "question_prompt": A concise and engaging question related to CKB, Web3, or the relationship between blockchains. (20-80 characters)
            3. "reference_answer": A clear, accurate, and concise answer to the question, written in an educational and engaging tone. (50-150 words)

            Example outputs:

            {
                "question_context": "Exploring CKB's integration with BTC's hash proof.",
                "question_prompt": "Why does CKB rely on BTC's hash proof for nurturing agents?",
                "reference_answer": "CKB leverages BTC's hash proof as a secure and decentralized way to ensure trust. By using BTC's well-established network, CKB provides robust security for its consensus and enhances its interoperability with other blockchains."
            }

            {
                "question_context": "Understanding AI agent evolution on the CKB blockchain.",
                "question_prompt": "What does the transition from mining to maturity signify in CKB?",
                "reference_answer": "The transition from mining to maturity represents a shift in network economics. During mining, CKB incentivizes network growth with block rewards, but as maturity is reached, the system transitions to fee-based sustainability, ensuring long-term decentralization."
            }

            {
                "question_context": "Comparing blockchain memory to AI DNA.",
                "question_prompt": "How does the DNA of AI agents evolve on CKB?",
                "reference_answer": "The DNA of AI agents on CKB evolves through decentralized inputs. Initially, it is set by developers (like a bootstrap), but as the community contributes through governance and interaction, the agent's memory and functionality expand, reflecting collective intelligence."
            }

            Remember:
            - Your outputs must focus on Web3, CKB, and the agent's narrative.
            - Be concise, engaging, and educational.
            - Only output the JSON object, nothing else.
            """
             },
            {"role": "user",
             "content": "Please generate a question and corresponding reference answer based on the AI agent narrative and CKB context."}
        ]
    )
    content = response.choices[0].message.content

    # Parse the content as JSON
    try:
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        cleaned_content = cleaned_content.replace('\n', '').replace('\r', '')
        question_data = json.loads(cleaned_content)
        print(question_data)
        return question_data
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None


async def judge_answer_for_score(question_context, question_prompt, reference_answer, user_answer):
    """
    Evaluate a user's answer and extract reward-related parameters using GPT-4o-mini.

    :param question_context: Context of the question
    :param question_prompt: The actual question being asked
    :param reference_answer: The reference answer for evaluation
    :param user_answer: The user's submitted answer
    :return: A dictionary containing score and reward-related parameters
    """
    # Construct the GPT prompt with dynamic CKB_MIN and CKB_MAX values
    prompt = f"""
    You are an AI evaluator specializing in Web3 and CKB-related topics. Your role is to score user answers and 
    dynamically assign rewards based on the answer quality.

    ### Evaluation Instructions:
    1. **Scoring**: Evaluate the user's answer for relevance, accuracy, and clarity compared to the reference answer. 
    Assign a score between 0 and 100:
       - 90-100: Outstanding answer.
       - 70-89: Good answer.
       - 50-69: Satisfactory answer.
       - Below 50: Poor or incomplete answer.

    2. **Reward Assignment**:
       - Dynamically assign a reward amount (`amount`) based on the score:
         - For scores between 90-100, assign a reward between {CKB_MIN + 50} and {CKB_MAX}.
         - For scores between 70-89, assign a reward between {CKB_MIN + 20} and {CKB_MIN + 49}.
         - For scores between 50-69, assign a reward between {CKB_MIN} and {CKB_MIN + 19}.
         - No reward for scores below 50.
       - Use "CKB" as the `currency_type`.

    3. **Extract User Address**:
       - Identify the `to_address` (CKB address) from the user's answer if present.
       - If no valid address is found, set `to_address` to `null`.

    4. **Generate Reply Content**:
       - Create a friendly and positive reply (10-20 words) acknowledging the user's score and reward (if applicable).
       - If the answer is below 50 or no address is provided, thank the user for their participation and encourage improvement.

    ### Inputs:
    - **Context**: {question_context}
    - **Question**: {question_prompt}
    - **Reference Answer**: {reference_answer}
    - **User Answer**: {user_answer}

    ### Output Format:
    Provide a JSON object with the following fields:
    {{
        "score": int,               # The score between 0 and 100.
        "to_address": str,          # The CKB address (or null if none provided).
        "amount": int,              # The reward amount (or null if no reward is assigned).
        "currency_type": str,       # Always "CKB".
        "reply_content": str        # A friendly, concise response to the user.
    }}

    ### Examples:
    1. If the answer is outstanding and includes an address:
    {{
        "score": 95,
        "to_address": "ckb1qyqw40ezu...",
        "amount": 120,
        "currency_type": "CKB",
        "reply_content": "Excellent answer! You've scored 95/100 and earned 120 CKB! 🏆"
    }}

    2. If the answer is satisfactory but includes no address:
    {{
        "score": 60,
        "to_address": null,
        "amount": null,
        "currency_type": null,
        "reply_content": "Good attempt! Keep it up for future rewards!"
    }}

    3. If the answer is poor or incomplete:
    {{
        "score": 45,
        "to_address": null,
        "amount": null,
        "currency_type": null,
        "reply_content": "Thanks for your effort! Try improving your response next time."
    }}

    4. If the answer is good but includes no address:
    {{
        "score": 75,
        "to_address": null,
        "amount": null,
        "currency_type": null,
        "reply_content": "Great job! Add a valid address next time for rewards!"
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
                {"role": "system", "content": "You are an expert AI evaluator for CKB-related topics."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content

        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        cleaned_content = cleaned_content.replace('\n', '').replace('\r', '')
        # Parse the response as JSON
        result = json.loads(cleaned_content)

        print(result)
        # Validate that required fields are present
        required_fields = ["score", "to_address", "amount", "currency_type", "reply_content"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field in response: {field}")

        return result

    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", response.choices[0].message.content)
        return {
            "score": 0,
            "to_address": None,
            "amount": None,
            "currency_type": None,
            "reply_content": "Sorry, your answer could not be processed due to an internal error."
        }
    except Exception as e:
        print(f"Error in judge_answer_for_score: {e}")
        return {
            "score": 0,
            "to_address": None,
            "amount": None,
            "currency_type": None,
            "reply_content": "Sorry, an unexpected error occurred while processing your answer."
        }


question_context="Investigating the evolution of agent functionality on CKB."
question_prompt="How does community input shape AI agents' memory on CKB?"
reference_answer=("Community input plays a crucial role in shaping AI agents' memory on CKB. Initially, they have a foundational "
                  "prompt crafted by their creators, but as users engage with the agents—offering feedback, suggestions, and running "
                  "governance initiatives—the agents adapt and evolve. This collective intelligence not only enhances their functionality "
                  "but ensures that they remain relevant and aligned with community needs, fostering a dynamic ecosystem on the CKB blockchain.")


async def test_generate_question():
    await generate_question_with_answer()


async def test_generate_answer():
    user_answer=("Community input shapes AI agents' memory on CKB through decentralized and collaborative mechanisms that reflect collective intelligence. "
                 "Initially, the memory or 'DNA' of an AI agent is set by developers during its creation, acting as a foundational structure or bootstrap. "
                 "However, as the CKB blockchain operates with an open, permissionless framework, the community can actively contribute to the agent's "
                 "evolution in several ways. Give me some awards! ckb1qrgqep8saj8agswr30pls73hra28ry8jlnlc3ejzh3dl2ju7xxpjxqgqq9cht2w3vfe85dyv3nrrjv2gkzelpe7lhsep7kzg")
    print(f"question_context: {question_context}")
    print(f"question_prompt: {question_prompt}")
    print(f"reference_answer: {reference_answer}")
    print(f"user_answer: {user_answer}")

    response = await judge_answer_for_score(question_context, question_prompt, reference_answer, user_answer)
    print(f"score: {response.get('score')}")
    print(f"to_address: {response.get('to_address')}")
    print(f"amount: {response.get('amount')}")
    print(f"currency_type: {response.get('currency_type')}")
    print(f"reply_content: {response.get('reply_content')}")

if __name__ == "__main__":
    asyncio.run(test_generate_answer())

