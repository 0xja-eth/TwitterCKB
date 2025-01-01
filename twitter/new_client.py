import os
from dotenv import load_dotenv
import tweepy

# load environment
load_dotenv()


class TwitterClient:
    def __init__(self):
        # load config
        self.consumer_key = os.getenv("ContriTweetAPIConsumerKey")
        self.consumer_secret = os.getenv("ContriTweetAPIKeySecret")
        self.client_id = os.getenv("ContriOAuthClientID")
        self.client_secret = os.getenv("ContriOAuthClientSecret")
        self.bearer_token = os.getenv("ContriAuthBearerToken")
        self.client_access_token = os.getenv("ContriAuthAccessToken")
        self.client_access_token_secret = os.getenv("ContriAuthAccessTokenSecret")
        self.access_token = os.getenv("TargetUserAccessToken")
        self.access_token_secret = os.getenv("TargetUserAccessTokenSecret")

        self.api_client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
        # Initialize Tweepy API (OAuth1 User Context)
        self.api_v1 = tweepy.API(
            auth=tweepy.OAuth2BearerHandler(
                bearer_token=self.bearer_token,
            )
        )

    # def authorize_user(self, access_token, access_token_secret):
    #     """
    #     auth, set access_token and access_token_secret。
    #     """
    #     self.access_token = access_token
    #     self.access_token_secret = access_token_secret
    #     self.api_client = tweepy.Client(
    #         bearer_token=self.bearer_token,
    #         consumer_key=self.consumer_key,
    #         consumer_secret=self.consumer_secret,
    #         access_token=self.access_token,
    #         access_token_secret=self.access_token_secret,
    #     )


n_client = TwitterClient()
