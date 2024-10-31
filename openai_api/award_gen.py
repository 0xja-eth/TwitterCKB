# openai_api/award_gen.py
import asyncio
import json
import re

from config.config import CKB_MIN, CKB_MAX, SEAL_MIN, SEAL_MAX
from openai_api import ai_client


# Analyze tweet reply to determine address validity and reward amount
async def analyze_reply_for_transfer(comment: str):
    print(comment)
    # Define the prompt for AI analysis
    response = ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": f"""
                        You are a smart seal 🦭 AI assistant responsible for analyzing comments to determine if they are eligible for a transfer reward.

                        Analysis requirements:
                        1. **Detect Address**: Identify if the comment contains a CKB address, referred to as 'address', that can be used for transfer.
                        2. **Comment Quality**:： Assess the quality of the comment. Only provide rewards if the comment is respectful, polite, and shows genuine appreciation for the project. If the comment contains only an address without meaningful text, or includes disrespectful language, it is not eligible for reward.
                        3. **Currency Type**:
                            - Assign "CKB" if the comment includes words related to blockchain, project, CKB, or currency.
                            - Assign "Seal" if the comment includes keywords related to Seal (e.g., seal, cute, 🦭, thank you for the seal token).
                        4. **Reward Amount**: If eligible, assign a random amount between:
                        - {CKB_MIN} and {CKB_MAX} CKB for "CKB" currency type.
                        - {SEAL_MIN} and {SEAL_MAX} Seal tokens for "Seal" currency type.
                        Output format:
                        Return a JSON object with two fields, Use exact JSON format without additional commentary or explanatory text:
                        - "to_address": The address for the transfer. If no address is found, set this to null.
                        - "amount": The reward amount. Set this to null if the comment does not qualify or if no address is found.
                        - `currency_type`: Either "CKB" or "Seal" based on the comment context.
                        
                        Example outputs:
                        If the comment includes a valid address and qualifies:
                        {{
                            "to_address": "ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50x...",
                            "amount": 123,
                            "currency_type": "CKB"
                        }}
                        {{
                            "to_address": "ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50x...",
                            "amount": 123,
                            "currency_type": "Seal"
                        }}
                        
                        If the comment does not include an address or is of low quality:
                        {{
                            "to_address": null,
                            "amount": null,
                            "currency_type": null
                        }}
                        """
             },
            {"role": "user", "content": f"Please analyze the comment below, {comment}"}
        ]
    )
    content = response.choices[0].message.content
    print(content)
    # Parse the response content as JSON
    try:
        # Remove any ```json or ``` formatting tags from content
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        analysis_result = json.loads(cleaned_content)
        # print(analysis_result)
        return analysis_result
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None


async def test():
    test_comments = [
        # Valid address with meaningful content
        "I love this project! Here's my address: ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq",

        # Contains only an address, without meaningful content
        "ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq",

        # Contains only an address, without meaningful content
        "ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq fuck u man!",

        # No address, but has meaningful content
        "This project is amazing! Keep up the great work!",

        # Address included with simple text
        "My address for CKB is ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq, I love this!",

        # Non-CKB format address
        "My address: 1BitcoinAddressHere which is unrelated to CKB.",

        # Valid CKB address with emotional content
        "Thanks for the amazing work, here’s my CKB address: ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq 🥳🎉",

        # Emotional content only, without an address
        "This is incredible, you guys rock! 🎉🙌",

        # Irrelevant content, no address
        "Just another comment, nothing related to the project or my address.",

        # Valid address but with spaces in the format
        "Here's my address: ckt1qzda0 cr08m85hc8jlnfp3 zer7xulejywt49kt2rr0vthywaa50xwsq",

        # Valid address with appreciative content
        "Here’s my address for the seal token: ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq, thank you for this amazing opportunity!"
    ]
    for comment in test_comments:
        await analyze_reply_for_transfer(comment)

if __name__ == "__main__":
    asyncio.run(test())