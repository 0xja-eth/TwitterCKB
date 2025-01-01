import os

import requests

from .new_client import TwitterClient


def post_tweet(client: TwitterClient, text: str) -> dict:
    """
    post_tweet(client, text) -> dict.
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        response = client.api_client.create_tweet(text=text)
        return {"tweet_id": response.data["id"], "message": "Tweet posted successfully!"}
    except Exception as e:
        raise RuntimeError(f"Error posting tweet: {e}")


def get_tweets(client: TwitterClient, max_results: int = 1) -> list:
    """
    get_tweets(client, max_results: int) -> list.
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        user_id = client.api_client.get_me().data.id
        tweets = client.api_client.get_users_tweets(id=user_id, max_results=max_results)
        return [{"id": tweet.id, "text": tweet.text} for tweet in tweets.data]
    except Exception as e:
        raise RuntimeError(f"Error fetching tweets: {e}")


def get_comments(client: TwitterClient, tweet_id: str, max_results: int = 10) -> list:
    """
    get_comments(client, tweet_id: str, max_results: int) -> list.
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        query = f"conversation_id:{tweet_id} is:reply"
        comments = client.api_client.search_recent_tweets(query=query, max_results=max_results)
        return [{"id": comment.id, "text": comment.text} for comment in comments.data]
    except Exception as e:
        raise RuntimeError(f"Error fetching comments: {e}")


def get_user_mention_comments(client: TwitterClient, user_id: str, start_time=None, end_time=None, max_results=30):
    """
    get_user_mentions(client, user_id: str, start_time=None, end_time=None) -> list.
    :param client:
    :param user_id:
    :param start_time:
    :param end_time:
    :return:
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        comments = client.api_client.get_users_mentions(id=user_id, start_time=start_time, end_time=end_time, max_results=max_results)
        return comments
    except Exception as e:
        raise RuntimeError(f"Error fetching comments: {e}")


def reply_comment(client: TwitterClient, comment_id: str, reply_text: str) -> dict:
    """
    reply_comment(client, comment_id, reply_text) -> dict.
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        response = client.api_client.create_tweet(text=reply_text, in_reply_to_tweet_id=comment_id)
        return {"reply_id": response.data["id"], "message": "Reply posted successfully!"}
    except Exception as e:
        raise RuntimeError(f"Error posting reply: {e}")


# Get tweet's Retweets
def get_retweets(client: TwitterClient, tweet_id: str, max_results: int = 100) -> list:
    """
    get_retweets(client, tweet_id, max_results) -> list.
    Fetches the Retweets for a given Tweet ID.
    :param client: TwitterClient instance.
    :param tweet_id: The ID of the Tweet for which Retweets are requested.
    :param max_results: The maximum number of Retweets to retrieve (default 100).
    :return: List of Retweets with user details.
    """
    if not client.api_client:
        raise ValueError("Client is not authorized. Please authorize first.")

    try:
        # Use Twitter API v2  Retweets
        endpoint = f"/2/tweets/{tweet_id}/retweets"  # Retweets API 的路径
        params = {
            "max_results": max_results,
            "user.fields": "id,username,name,verified,profile_image_url"
        }

        # 调用 BaseClient 的 request 方法
        response = client.api_client.request(
            method="GET",
            route=endpoint,  # 确保路径正确
            params=params,
            user_auth=False  # 如果需要用户身份认证，可设置为 True
        )

        # 检查响应并返回结果
        if isinstance(response, requests.Response) and response.status_code == 200:
            data = response.json()
            retweets = []
            for user in data.get("data", []):
                retweets.append({
                    "user_id": user.get("id"),
                    "username": user.get("username"),
                    "name": user.get("name"),
                    "verified": user.get("verified"),
                    "profile_image_url": user.get("profile_image_url")
                })
            return retweets
        else:
            # 如果 response 不是有效的成功响应，抛出错误
            raise RuntimeError(f"Failed to fetch retweets: {response.status_code} - {response.text}")

    except Exception as e:
        raise RuntimeError(f"Error fetching retweets: {e}")


def get_retweets_list(tweet_id: str, max_results: int = 100) -> list:
    """
    Fetches the Retweets (Tweet objects) for a given Tweet ID using Twitter API v2.

    :param tweet_id: The ID of the Tweet for which Retweets are requested.
    :param bearer_token: OAuth 2.0 Bearer Token for authentication.
    :param max_results: The maximum number of Retweets to retrieve (default 100).
    :return: List of Retweets with Tweet details.
    """
    # API URL
    url = f"https://api.x.com/2/tweets/{tweet_id}/retweets"

    bear_token = os.getenv("ContriAuthBearerToken")

    # Request headers
    headers = {
        "Authorization": f"Bearer {bear_token}",
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15'
    }

    # Query parameters
    params = {
        "max_results": max_results,
        "tweet.fields": "id,text,author_id,created_at,public_metrics",
    }

    try:
        # 发送 GET 请求
        response = requests.get(url, headers=headers, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()
            retweets = []
            for retweet in data.get("data", []):
                retweets.append({
                    "id": retweet.get("id"),
                    "text": retweet.get("text"),
                    "author_id": retweet.get("author_id"),
                    "created_at": retweet.get("created_at"),
                    "public_metrics": retweet.get("public_metrics"),
                })
            return retweets
        else:
            # 如果响应非 200，抛出错误
            raise RuntimeError(
                f"Failed to fetch retweets: {response.status_code} - {response.text}"
            )

    except requests.exceptions.RequestException as e:
        # 处理连接错误
        raise RuntimeError(f"Error fetching retweets: {e}")
