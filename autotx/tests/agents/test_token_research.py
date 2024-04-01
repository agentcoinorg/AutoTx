from autotx.agents.TokenResearchAgent import TokenResearchAgent
from crewai import Task

agent = TokenResearchAgent()


def test_price_change_information():
    task = Task(
        description="What's the 24 hours price change of Starknet (STRK)",
        agent=agent,
        expected_output="The price change of STRK in the last 24 hours",
    )
    response = agent.execute_task(task)
    assert "STRK" in response


def test_token_general_information():
    agent = TokenResearchAgent()
    task = Task(
        description="What is Polkadot's token?",
        agent=agent,
        expected_output="Information about polkadot's token",
    )
    response = agent.execute_task(task)
    assert "Polkadot is" in response

def test_check_liquidity():
    agent = TokenResearchAgent()
    task = Task(
        description="How much liquidity does UNI have?",
        agent=agent,
        expected_output="Information about UNI's token liquidity",
    )
    response = agent.execute_task(task)
    assert "The liquidity of the UNI token" in response

def test_get_top_5_tokens_from_base():
    agent = TokenResearchAgent()
    task = Task(
        description="What are the top 5 tokens on Base chain?",
        agent=agent,
        expected_output="Top 5 tokens from base chain",
    )
    response = agent.execute_task(task)
    assert "The top 5 tokens" in response

def test_get_top_5_most_traded_tokens_from_l1():
    agent = TokenResearchAgent()
    task = Task(
        description="What are the 5 most traded L1 tokens?",
        agent=agent,
        expected_output="Top 5 most traded tokens from L1",
    )
    response = agent.execute_task(task)
    assert "5 most traded" in response