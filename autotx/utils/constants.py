from dotenv import load_dotenv
load_dotenv()
import os

OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", None)
LIFI_API_KEY = os.environ.get("LIFI_API_KEY", None)
ALCHEMY_API_KEY = os.environ.get("ALCHEMY_API_KEY")
MAINNET_DEFAULT_RPC = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"