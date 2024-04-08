from langchain_openai import ChatOpenAI
from autotx.utils.constants import OPENAI_MODEL_NAME

open_ai_llm = ChatOpenAI(temperature=0, model=OPENAI_MODEL_NAME) # type: ignore