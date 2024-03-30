# from autotx.AutoTx import AutoTx
from autotx.agents.TokenResearchAgent import TokenResearchAgent
from crewai import Task
from autotx.patch import patch_langchain

patch_langchain()


def test_token_research_agent():
    agent = TokenResearchAgent()
    task = Task(
        description="What's the 24 hours price change of ETH",
        agent=agent,
        expected_output="The price change of ETH in the last 24 hours"
    )
    response = agent.execute_task(task)
    print(response)
