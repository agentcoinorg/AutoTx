import os
from textwrap import dedent
import pytest
from autotx.agents import ResearchTokensAgent
from autotx.agents.ResearchTokensAgent import (
    filter_token_list_by_network,
    get_coingecko,
)
from autogen import AssistantAgent, UserProxyAgent, GroupChatManager
import autogen

from autotx.utils.constants import OPENAI_API_KEY, OPENAI_MODEL_NAME
from autotx.utils.ethereum.networks import ChainId

@pytest.fixture()
def user_proxy_agent() -> UserProxyAgent:
    llm_config = { "cache_seed": None, "config_list": [{"model": OPENAI_MODEL_NAME, "api_key": OPENAI_API_KEY}]}
    user_proxy_agent = UserProxyAgent(
        name="user_proxy_agent",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=20,
        system_message=f"You are a user proxy. You will be interacting with the agents to accomplish the tasks.",
        llm_config=llm_config,
        code_execution_config=False,
    )
    return user_proxy_agent

@pytest.fixture()
def manager(auto_tx, user_proxy_agent) -> GroupChatManager:
    get_llm_config = lambda: { "cache_seed": None, "config_list": [{"model": OPENAI_MODEL_NAME, "api_key": OPENAI_API_KEY}]}
   
    verifier_agent = AssistantAgent(
        name="verifier",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        system_message=dedent(
                """
                You are an expert in verifiying if user goals are met.
                You analyze chat and respond with TERMINATE if the goal is met.
                You can consider the goal met if the other agents have prepared the necessary transactions.
                """
            ),
        llm_config=get_llm_config(),
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    token_research_agent = ResearchTokensAgent.build_agent_factory()(auto_tx, user_proxy_agent, get_llm_config()).autogen_agent

    groupchat = autogen.GroupChat(agents=[user_proxy_agent, verifier_agent, token_research_agent], messages=[], max_round=20)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())

    return manager

def test_price_change_information(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    token_information = get_coingecko().coins.get_id(
        id="starknet",
        localization=False,
        tickers=False,
        community_data=False,
        sparkline=False,
    )
    prompt = "What's the 24 hours price change of Starknet (STRK)"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt, 
        summary_method="reflection_with_llm"
    )

    price_change = token_information["market_data"]["price_change_percentage_24h"]
    price_change_rounded = round(price_change, 2)

    assert (
        str(price_change) in result.summary or str(price_change_rounded) in result.summary
    )

def test_get_token_exchanges(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    prompt = "Where can I buy BRETT?"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt, 
        summary_method="reflection_with_llm"
    )

    assert "SushiSwap V3" in result.summary

def test_check_liquidity(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    token_information = get_coingecko().coins.get_id(
        id="uniswap",
        localization=False,
        tickers=False,
        community_data=False,
        sparkline=False,
    )
    prompt = "How much liquidity does UNI have?"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt, 
        summary_method="reflection_with_llm"
    )

    assert (
        "${:,}".format(token_information["market_data"]["total_volume"]["usd"])
        in result.summary
    )

def test_get_top_5_tokens_from_base(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="base-ecosystem"
    )
    prompt = "What are the top 5 tokens on Base chain?"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt,
        summary_method="reflection_with_llm"
    )

    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in result.summary.lower()

def test_get_top_5_most_traded_tokens_from_l1(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="layer-1", order="volume_desc"
    )
    prompt = "What are the top 5 most traded tokens on L1"
    
    result = user_proxy_agent.initiate_chat(
        manager, message=prompt,
        summary_method="reflection_with_llm"
    )

    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in result.summary.lower()

def test_get_top_5_memecoins(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    prompt = "What are the top 5 meme coins"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt, 
        summary_method="reflection_with_llm"
    )

    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in result.summary.lower()

def test_get_top_5_memecoins_in_optimism(user_proxy_agent: UserProxyAgent, manager: GroupChatManager):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    prompt = "What are the top 5 meme coins in optimism"

    result = user_proxy_agent.initiate_chat(
        manager, message=prompt, 
        summary_method="reflection_with_llm"
    )

    tokens = filter_token_list_by_network(tokens, ChainId.OPTIMISM.name)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in result.summary.lower()
