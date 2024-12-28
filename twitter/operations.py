
from new_client import TwitterClient


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


def get_user_mention_comments(client: TwitterClient, user_id: str, start_time=None, end_time=None, max_results=30) -> list:
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
        comments = client.api_client.get_user_comments(user_id=user_id, start_time=start_time, end_time=end_time, max_results=max_results)
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



