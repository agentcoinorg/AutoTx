from langchain_openai import ChatOpenAI
import os

open_ai_llm = ChatOpenAI(temperature=0, model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")) # type: ignore