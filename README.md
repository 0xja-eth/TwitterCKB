
# TwitterCKB

TwitterCKB is an intelligent, blockchain-based seal assistant operating on the Nervos network. The "Seal Agent" interacts with users on Twitter, managing assets in both CKB and Seal tokens, sending gratitude tweets, distributing tokens, and posting status emoticons to provide real-time balance feedback, all while ensuring user data privacy.

## Project Overview

### Key Features

- **Automatic Gratitude Tweets**: Posts a thank-you tweet when receiving CKB or Seal tokens.
- **Token Rewards**: Randomly sends tokens (CKB or Seal) to users who interact with specific comments or hashtags.
- **Scheduled Status Emoticons**: Posts hourly status emoticons reflecting balance, keeping the seal's followers engaged.
- **Secure Transfers**: Provides safe CKB or Seal transfers based on user requests, ensuring transparency and data privacy.

### Core Technologies

- **Python**: The primary programming language.
- **Asyncio**: Handles asynchronous operations like scheduled tweets and real-time interactions.
- **Twikit**: Utilized for automating tweets and Twitter interactions.
- **Nervos CKB SDK**: To interact with the Nervos blockchain for token management and transfers.
- **OpenAI GPT Model**: Generates content for tweets, emoticons, and responses.

## Installation

### Prerequisites

- **Python 3.9+**
- **Pip (Python Package Installer)**

### Clone the Repository

```bash
git clone https://github.com/Gary-666/TwitterCKB.git
cd TwitterCKB
```
### Package
```bash
pyinstaller --onefile  client.py
```

## Configuration Parameters
To run TwitterCKB, you need to set several environment variables. These variables include API keys, authentication details, Redis configurations, and other necessary parameters. Below is an explanation of each parameter:
- **OPENAI_API_KEY**: Your API key for OpenAI, used to generate tweets, responses, and emoticons.
  
- **TWITTER_USERNAME**: Your Twitter account username. Required for authenticating interactions with Twitter.

- **TWITTER_EMAIL**: Your Twitter account email. Used in conjunction with the username and password for Twitter authentication.

- **TWITTER_PASSWORD**: Your Twitter account password. Essential for logging in and managing tweets automatically.

- **HTTP_PROXY**: The HTTP proxy address to connect with OpenAI. Set this if you need to route OpenAI API requests through a proxy.

- **HTTPS_PROXY**: The HTTPS proxy address to connect with OpenAI, similar to the HTTP proxy but for secure connections.

- **AI_TOKEN**: Your private key for sending CKB tokens. This key manages transactions on the blockchain.

- **REDIS_HOST**: The hostname or IP address of your Redis server, which is used to store data for processing replies and managing transaction states.

- **REDIS_PORT**: The port on which your Redis server is running. The default Redis port is usually `6379`.

- **REDIS_PASSWORD**: Your Redis password. Required if your Redis server is password-protected.

- **REDIS_DB**: The specific Redis database number you want to use. Redis databases are numbered from 0 to 15 by default.

- **REDIS_TLS**: Set to `true` if your Redis server uses TLS for secure communication.

- **REDIS_SNI**: If applicable, provide the Server Name Indication (SNI) for Redis TLS connections.

- **OUR_ADDRESS**: The Nervos CKB blockchain address where your tokens are held. Used for managing token transfers.

- **COOKIES_JSON**: Path to a JSON file with Twitter cookies for session management. Necessary if you need cookie-based authentication with Twitter.

- **SEAL_XUDT_ARGS**: The XUDT arguments for Seal tokens, used when sending Seal tokens on the Nervos network.

- **BASE_URL**: The base URL for your server’s API endpoints. This URL is used for all API requests from the client to the server.

Setting these parameters correctly is essential for seamless functionality of the TwitterCKB application. Be sure to review and confirm each parameter before running the application.


