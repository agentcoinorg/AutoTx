import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", None)
LIFI_API_KEY = os.environ.get("LIFI_API_KEY", None)