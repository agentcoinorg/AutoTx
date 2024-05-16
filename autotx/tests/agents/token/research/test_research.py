from autotx.agents.ResearchTokensAgent import (
    filter_token_list_by_network,
    get_coingecko,
)

from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import ChainId

def get_top_token_addresses_by_market_cap(category: str, network: str, count: int, auto_tx) -> list[ETHAddress]:
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category=category, per_page=250)
    tokens_in_network = filter_token_list_by_network(
        tokens, network
    )

    return [ETHAddress(auto_tx.network.tokens[token["symbol"].lower()]) for token in tokens_in_network[:count]]

def test_price_change_information(auto_tx):
    token_information = get_coingecko().coins.get_id(
        id="starknet",
        localization=False,
        tickers=False,
        community_data=False,
        sparkline=False,
    )
    prompt = "What's the 24 hours price change of Starknet (STRK)?"

    result = auto_tx.run(prompt, non_interactive=True)

    price_change = token_information["market_data"]["price_change_percentage_24h"]
    price_change_rounded = round(price_change, 2)

    assert (
        str(price_change) in "\n".join(result.info_messages).lower() or str(price_change_rounded) in "\n".join(result.info_messages).lower()
    )

def test_get_top_5_tokens_from_base(auto_tx):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="base-ecosystem"
    )
    prompt = "What are the top 5 tokens on Base chain?"

    result = auto_tx.run(prompt, non_interactive=True)

    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in "\n".join(result.info_messages).lower()

def test_get_top_5_most_traded_tokens_from_l1(auto_tx):
    tokens = get_coingecko().coins.get_markets(
        vs_currency="usd", category="layer-1", order="volume_desc"
    )
    prompt = "What are the top 5 most traded Layer 1 tokens on all networks?"
    
    result = auto_tx.run(prompt, non_interactive=True)

    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in "\n".join(result.info_messages).lower()

def test_get_top_5_memecoins(auto_tx):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    tokens_in_network = filter_token_list_by_network(
        tokens, "MAINNET"
    )

    prompt = "What are the top 5 meme coins on my network?"

    result = auto_tx.run(prompt, non_interactive=True)

    for token in tokens_in_network[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in "\n".join(result.info_messages).lower()

def test_get_top_5_memecoins_in_optimism(auto_tx):
    tokens = get_coingecko().coins.get_markets(vs_currency="usd", category="meme-token")
    prompt = "What are the top 5 meme coins on Optimism?"

    result = auto_tx.run(prompt, non_interactive=True)

    tokens = filter_token_list_by_network(tokens, ChainId.OPTIMISM.name)
    for token in tokens[:5]:
        symbol: str = token["symbol"]
        assert symbol.lower() in "\n".join(result.info_messages).lower()
