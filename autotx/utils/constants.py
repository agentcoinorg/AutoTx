import os

OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", None)