from crewai import Task, Agent
import pytest

from autotx.agents.ResearchTokensAgent import ResearchTokensAgent

@pytest.fixture()
def token_research_agent() -> Agent:
    return ResearchTokensAgent()

def test_price_change_information(token_research_agent: Agent):
    task = Task(
        description="What's the 24 hours price change of Starknet (STRK)",
        agent=token_research_agent,
        expected_output="The price change of STRK in the last 24 hours",
    )
    response = token_research_agent.execute_task(task)
    assert "STRK" in response

def test_token_general_information(token_research_agent: Agent):
    task = Task(
        description="What is Polkadot's token?",
        agent=token_research_agent,
        expected_output="Information about polkadot's token",
    )
    response = token_research_agent.execute_task(task)
    assert "Polkadot is" in response
    assert "DOT" in response or "dot" in response

def test_get_token_exchanges(token_research_agent: Agent):
    task = Task(
        description="Where can I buy BRETT?",
        agent=token_research_agent,
        expected_output="Exchanges where BRETT can be bought",
    )
    response = token_research_agent.execute_task(task)
    assert "SushiSwap V3 (Base)" in response or "Raydium" in response


def test_check_liquidity(token_research_agent: Agent):
    task = Task(
        description="How much liquidity does UNI have?",
        agent=token_research_agent,
        expected_output="Liquidity of UNI",
    )
    response = token_research_agent.execute_task(task)
    assert "The liquidity" in response

def test_get_top_5_tokens_from_base(token_research_agent: Agent):
    task = Task(
        description="What are the top 5 tokens on Base network?",
        agent=token_research_agent,
        expected_output="Top 5 tokens from base network",
    )
    response = token_research_agent.execute_task(task)
    assert "The top 5 tokens" in response

def test_get_top_5_most_traded_tokens_from_l1(token_research_agent: Agent):
    task = Task(
        description="What are the 5 most traded L1 tokens?",
        agent=token_research_agent,
        expected_output="Top 5 most traded tokens from L1",
    )
    response = token_research_agent.execute_task(task)
    assert "5 most traded" in response


def test_get_top_5_memecoins(token_research_agent: Agent):
    task = Task(
        description="What are the top 5 meme coins",
        agent=token_research_agent,
        expected_output="Top 5 meme coins",
    )
    response = token_research_agent.execute_task(task)
    assert "top 5 meme coins" in response or "top 5 meme tokens" in response


def test_get_top_5_memecoins_in_optimism(token_research_agent: Agent):
    task = Task(
        description="What are the top 5 meme coins in optimism",
        agent=token_research_agent,
        expected_output="Top 5 meme coins in optimism",
    )
    response = token_research_agent.execute_task(task)
    assert "top 5 meme coins" in response or "top 5 meme tokens" in response
    assert "Optimism" in response or "optimism" in response
