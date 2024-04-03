import json
import os
from textwrap import dedent
from typing import Callable, Union
from crewai import Agent
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from crewai_tools import BaseTool
from gnosis.eth import EthereumNetwork, EthereumNetworkNotSupported
import coingecko

COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP = {
    EthereumNetwork.MAINNET: "ethereum",
    EthereumNetwork.OPTIMISM: "optimistic-ethereum",
    EthereumNetwork.POLYGON: "polygon-pos",
    EthereumNetwork.BASE_MAINNET: "base",
    EthereumNetwork.ARBITRUM_ONE: "arbitrum-one",
    EthereumNetwork.GNOSIS: "xdai",
}

def get_coingecko():
    return coingecko.CoinGeckoDemoClient(api_key=os.getenv("COINGECKO_API_KEY"))


def get_tokens_and_filter_per_network(
    chain_id: int,
) -> dict[str, Union[str, dict[str, str]]]:
    network = EthereumNetwork(chain_id)
    coingecko_network_key = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(network)
    if coingecko_network_key == None:
        raise EthereumNetworkNotSupported(
            f"Network with chain id {chain_id} not supported"
        )

    token_list_with_addresses = get_coingecko().coins.get_list(include_platform=True)
    return [
        token
        for token in token_list_with_addresses
        if coingecko_network_key in token["platforms"]
    ]


class TokenSymbolToTokenId(BaseTool):
    name: str = "token_symbol_to_token_id"
    description: str = dedent(
        """
        Fetch token list and returns token ID based on symbol given

        Args:
            token_symbol (list[str]): Symbol of tokens,
            chain_id (int): The network ID where tokens should be
        """
    )

    def _run(self, token_symbols: list[str], chain_id: int):
        token_list = get_tokens_and_filter_per_network(chain_id)
        token_symbols_in_lower = [symbol.lower() for symbol in token_symbols]
        return json.dumps(
            [
                item["id"]
                for item in token_list
                if item["symbol"] in token_symbols_in_lower
            ]
        )


class GetTokenInformation(BaseTool):
    name: str = "get_token_information"
    description: str = dedent(
        """
        Retrieve token information (current price, market cap and price change percentage)

        Args:
            token_id (str): ID of token
        """
    )

    def _run(self, token_id: str):
        token_information = get_coingecko().coins.get_id(
            id=token_id,
            localization=False,
            tickers=False,
            community_data=False,
            sparkline=False,
        )
        return json.dumps(
            {
                "name": token_information["name"],
                "symbol": token_information["symbol"],
                "description": token_information["description"]["en"],
                "current_price_in_usd": token_information["market_data"][
                    "current_price"
                ]["usd"],
                "market_cap_in_usd": token_information["market_data"]["market_cap"][
                    "usd"
                ],
                "total_volume_last_24h": token_information["market_data"][
                    "total_volume"
                ]["usd"],
                "price_change_percentage_24h": token_information["market_data"][
                    "price_change_percentage_24h"
                ],
                "price_change_percentage_7d": token_information["market_data"][
                    "price_change_percentage_7d"
                ],
                "price_change_percentage_30d": token_information["market_data"][
                    "price_change_percentage_30d"
                ],
                "price_change_percentage_60d": token_information["market_data"][
                    "price_change_percentage_60d"
                ],
                "price_change_percentage_200d": token_information["market_data"][
                    "price_change_percentage_200d"
                ],
                "price_change_percentage_1y": token_information["market_data"][
                    "price_change_percentage_1y"
                ],
            }
        )


class GetAvailableCategories(BaseTool):
    name: str = "get_available_categories"
    description: str = dedent(
        """
        Retrieve all categories
        """
    )

    def _run(self):
        categories = get_coingecko().categories.get_list()
        return json.dumps([category["category_id"] for category in categories])


class GetTokensBasedOnCategory(BaseTool):
    name: str = "get_tokens_based_on_category"
    description: str = dedent(
        """
        Retrieve all tokens from a given category

        Args:
            category (str): Category to retrieve tokens
            sort_by (str): Sort tokens by field. It can be: "volume_desc" | "volume_asc" | "market_cap_desc" | "market_cap_asc"
                "market_cap_desc" should be the default if none is defined
            limit (int): The number of tokens to return from the category
            chain_id (int): The network ID where tokens should be
        """
    )

    def _run(self, category: str, sort_by: str, limit: int, chain_id: int):
        tokens_in_category = get_coingecko().coins.get_markets(
            vs_currency="usd",
            category=category,
            order=sort_by,
            price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            per_page=250,
        )

        tokens_in_category_map = {
            category["id"]: category for category in tokens_in_category
        }

        tokens_in_category_in_desired_network = [
            {**token, **tokens_in_category_map[token["id"]]}
            for token in get_tokens_and_filter_per_network(chain_id)
            if token["id"] in tokens_in_category_map
        ]

        tokens = [
            {
                "symbol": token["symbol"],
                "market_cap": token["market_cap"],
                "total_volume_last_24h": token["total_volume"],
                "price_change_percentage_1h": token[
                    "price_change_percentage_1h_in_currency"
                ],
                "price_change_percentage_24h": token[
                    "price_change_percentage_24h_in_currency"
                ],
                "price_change_percentage_7d": token[
                    "price_change_percentage_7d_in_currency"
                ],
                "price_change_percentage_14d": token[
                    "price_change_percentage_14d_in_currency"
                ],
                "price_change_percentage_30d": token[
                    "price_change_percentage_30d_in_currency"
                ],
                "price_change_percentage_200d": token[
                    "price_change_percentage_200d_in_currency"
                ],
                "price_change_percentage_1y": token[
                    "price_change_percentage_1y_in_currency"
                ],
            }
            for token in tokens_in_category_in_desired_network[:limit]
        ]

        return json.dumps(tokens)


class TokenExchanges(BaseTool):
    name: str = "get_exchanges_where_token_can_be_traded"
    description: str = dedent(
        """
        Retrieve exchanges where token can be traded
        Args:
            token_id (str): ID of token
        """
    )

    def _run(self, token_id: str):
        tickers = get_coingecko().coins.get_tickers(id=token_id)["tickers"]
        market_names = {item["market"]["name"] for item in tickers}
        return list(market_names)


class ResearchTokensAgent(AutoTxAgent):
    def __init__(self, autotx: AutoTx):
        if os.getenv("COINGECKO_API_KEY") == None:
            raise "You must add a value to COINGECKO_API_KEY key in .env file"

        super().__init__(
            name="token-researcher",
            role="Highly specialized AI assistant with expertise in researching cryptocurrencies and analyzing the market",
            goal=f"Help users with real-time analytics and trend predictions. By default, you must do investigation based on network {autotx.network.network.name} with chain id {autotx.network.network.value}, unless explicitly told to use other one",
            backstory="Designed to address the challenge of navigating the complex and fast-paced world of cryptocurrencies",
            tools=[
                GetTokenInformation(),
                TokenSymbolToTokenId(),
                GetTokensBasedOnCategory(),
                GetAvailableCategories(),
                TokenExchanges(),
            ],
        )


def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> ResearchTokensAgent:
        return ResearchTokensAgent(autotx)

    return agent_factory
