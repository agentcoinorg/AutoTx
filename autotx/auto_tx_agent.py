from crewai import Agent
from langchain_openai import ChatOpenAI
from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.llm import open_ai_llm
from crewai import Agent

class AutoTxAgent(Agent):
    name: str
    def __init__(
            self, 
            name: str, 
            role: str, 
            goal: str, 
            backstory: str, 
            tools: list[AutoTxTool], 
            llm: ChatOpenAI = open_ai_llm, 
            verbose: bool = True, 
            allow_delegation: bool = False
    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            llm=llm,
            verbose=verbose,
            allow_delegation=allow_delegation,
        )