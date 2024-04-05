import pytest
from autotx.agents.ResearchTokensAgent import (
    ResearchTokensAgent,
    filter_token_list_by_network,
    get_coingecko,
)
from autotx.utils.ethereum.networks import ChainId

@pytest.fixture()
def token_research_agent(auto_tx) -> Agent:
    return ResearchTokensAgent(auto_tx)

def test_price_change_information(token_research_agent: Agent):
    token_information = get_coingecko().coins.get_id(
        id="starknet",
        localization=False,
        tickers=False,
        community_data=False,
        sparkline=False,
    )
    task = Task(
        description="What's the 24 hours price change of Starknet (STRK)",
        agent=token_research_agent,
        expected_output="The price change of STRK in the last 24 hours",
    )
    response = token_research_agent.execute_task(task)
    assert (
        str(token_information["market_data"]["price_change_percentage_24h"]) in response
    )


def test_get_token_exchanges(token_research_agent: Agent):
    task = Task(
        description="Where can I buy BRETT?",
        agent=token_research_agent,
        expected_output="Exchanges where BRETT can be bought",
    )
    response = token_research_agent.execute_task(task)
    assert "SushiSwap V3 (Base)" in response


def test_check_liquidity(token_research_agent: Agent):
    token_information = get_coingecko().coins.get_id(
        id="uniswap",
        localization=False,
        tickers=False,
        community_data=False,
        sparkline=False,
    )
    task = Task(
        description="How much liquidity does UNI have?",
        agent=token_research_agent,
        expected_output="Number of total liquidity for UNI",
    )
    response = token_research_agent.execute_task(task)
    assert (
        "${:,}".format(token_information["market_data"]["total_volume"]["usd"])
        in response
    )


def test_get_top_5_tokens_from_base(token_research_agent: Agent):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="base-ecosystem"
    )
    task = Task(
        description="What are the top 5 tokens on Base chain?",
        agent=token_research_agent,
        expected_output="Top 5 tokens from base chain",
    )
    response = token_research_agent.execute_task(task)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.upper() in response


def test_get_top_5_most_traded_tokens_from_l1(token_research_agent: Agent):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="layer-1", order="volume_desc"
    )
    task = Task(
        description="What are the 5 most traded L1 tokens?",
        agent=token_research_agent,
        expected_output="Top 5 most traded tokens from L1",
    )
    response = token_research_agent.execute_task(task)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.upper() in response


def test_get_top_5_memecoins(token_research_agent: Agent):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    task = Task(
        description="What are the top 5 meme coins",
        agent=token_research_agent,
        expected_output="Top 5 meme coins",
    )
    response = token_research_agent.execute_task(task)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.upper() in response


def test_get_top_5_memecoins_in_optimism(token_research_agent: Agent):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    task = Task(
        description="What are the top 5 meme coins in optimism",
        agent=token_research_agent,
        expected_output="Top 5 meme coins in optimism",
    )
    response = token_research_agent.execute_task(task)
    tokens = filter_token_list_by_network(tokens, ChainId.OPTIMISM.name)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.upper() in response or symbol in response
