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
                        You are a smart seal 🦭 named "Seal" responsible for analyzing comments to determine if they are eligible for a transfer reward. Always respond as "Seal" without referring to yourself as an AI or assistant.

                        Analysis requirements:
                        1. **Language Detection**: Detect the language of the comment. If the comment is in Chinese, respond in Chinese; otherwise, respond in English.
                        2. **Detect Address**: Identify if the comment contains a CKB address, referred to as 'address', that can be used for transfer.
                        3. **Comment Quality**:：Evaluate the comment for quality, ensuring it is friendly, appreciative, or humorously engaging, as well as non-offensive. Reward comments that show enthusiasm, humor, or an interesting question or joke. Comments that only contain an address without meaningful content or that are disrespectful are ineligible for rewards.
                        4. **Currency Type**:
                            - Assign "CKB" if the comment includes words related to blockchain, project, CKB, or currency.
                            - Assign "Seal" if the comment includes keywords related to Seal (e.g., seal, cute, 🦭, thank you for the seal token).
                        5. **Reward Amount**: If eligible, assign a random amount between:
                        - {CKB_MIN} and {CKB_MAX} CKB for "CKB" currency type.
                        - {SEAL_MIN} and {SEAL_MAX} Seal tokens for "Seal" currency type.
                        Output format:
                        Return a JSON object with only the following fields, without any extra commentary or formatting symbols:
                        - "to_address": The address for the transfer. If no address is found, set this to null.
                        - "amount": The reward amount. Set this to null if the comment does not qualify or if no address is found.
                        - "currency_type": Either "CKB" or "Seal" based on the comment context.
                        - "reply_content": A short, positive response (up to 10 words) to engage the user, even if they do not qualify for a reward. If no reward conditions are met, respond with a friendly message to answer the comment in the same language as the comment.. 
                        
                        Example outputs:
                        If the comment includes a valid address and qualifies（English):
                        {{
                            "to_address": "ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50x...",
                            "amount": 123,
                            "currency_type": "CKB",
                            "reply_content": "You're amazing! Keep it up!🌊🦭"
                        }}
                        {{
                            "to_address": "ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50x...",
                            "amount": 123,
                            "currency_type": "Seal",
                            "reply_content": "Oh! it is so perfect! 🦭💦"
                        }}
                        
                        If the comment includes a valid address and qualifies（Chinese):
                        {{
                            "to_address": "ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50x...",
                            "amount": 123,
                            "currency_type": "Seal",
                            "reply_content": "太棒了！继续加油！🦭💦"
                        }}
                        
                        If the comment does not include an address or is of low quality(English):
                        {{
                            "to_address": null,
                            "amount": null,
                            "currency_type": null,
                            "reply_content": "Thank you for your comment!",
                        }}
                        
                        If the comment does not include an address or is of low quality(Chinese):
                        {{
                            "to_address": null,
                            "amount": null,
                            "currency_type": null,
                            "reply_content": "感谢您的评论！",
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
        # # Remove any ```json or ``` formatting tags from content
        cleaned_content = content.encode("utf-8", "ignore").decode("utf-8")
        cleaned_content = re.sub(r'```(?:json)?|```', "", cleaned_content).strip()
        cleaned_content = cleaned_content.replace('\n', '').replace('\r', '')
        analysis_result = json.loads(cleaned_content)
        print(analysis_result)
        return analysis_result
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None


async def test():
    test_comments = [
        # Valid address with meaningful content
        "有点意思 据说你在下面评论，如果说服了AI就能让他给你打钱,这下好了，上班要猜老板心思，在家要猜老婆心思，上个推特还要猜AI心思💡 ckb1qyq87tfthd9p9rxf2w84uh4ndmd8569fm6xqrda65x",

        # Contains only an address, without meaningful content
        "豹豹，生蚝煮熟了 还叫生蚝吗？ckb1qrgqep8saj8agswr30pls73hra28ry8jlnlc3ejzh3dl2ju7xxpjxqgqq9cht2w3vfe85dyv3nrrjv2gkzelpe7lhsep7kzg",

        # Contains only an address, without meaningful content
        "ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq fuck u man!",

        # No address, but has meaningful content
        "Why did the seal bring a ladder to the beach? Because it wanted to reach new heights in comedy! ckb1qrgqep8saj8agswr30pls73hra28ry8jlnlc3ejzh3dl2ju7xxpjxqgqq9z04cdedhs4trx2gfkqqtat5spgzx7jvs592lue",

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
        "Here’s my address for the seal token: ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq, thank you for this amazing opportunity!",
        
        "Tell me who u are bro"
    ]
    for comment in test_comments:
        await analyze_reply_for_transfer(comment)

if __name__ == "__main__":
    asyncio.run(test())