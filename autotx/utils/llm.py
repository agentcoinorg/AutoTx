from langchain_openai import ChatOpenAI

open_ai_llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview") # type: ignore
