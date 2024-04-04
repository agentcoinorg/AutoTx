import json
import os
from textwrap import dedent
from typing import Callable, Optional, Union
from crewai import Agent
from web3 import Web3
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from crewai_tools import BaseTool
from gnosis.eth import EthereumNetwork, EthereumNetworkNotSupported
from coingecko import GeckoAPIException, CoinGeckoDemoClient

from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_AS_STRING

COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP = {
    EthereumNetwork.MAINNET: "ethereum",
    EthereumNetwork.OPTIMISM: "optimistic-ethereum",
    EthereumNetwork.POLYGON: "polygon-pos",
    EthereumNetwork.BASE_MAINNET: "base",
    EthereumNetwork.ARBITRUM_ONE: "arbitrum-one",
    EthereumNetwork.GNOSIS: "xdai",
}


def get_coingecko():
    return CoinGeckoDemoClient(api_key=os.getenv("COINGECKO_API_KEY"))


def get_tokens_and_filter_per_network(
    network_name: str,
) -> dict[str, Union[str, dict[str, str]]]:
    network = EthereumNetwork[network_name]
    coingecko_network_key = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(network)
    if coingecko_network_key == None:
        raise EthereumNetworkNotSupported(f"Network {network_name} not supported")

    token_list_with_addresses = get_coingecko().coins.get_list(include_platform=True)
    return [
        token
        for token in token_list_with_addresses
        if coingecko_network_key in token["platforms"]
    ]


class GetTokenInformation(BaseTool):
    name: str = "get_token_information"
    description: str = dedent(
        """
        Retrieve token information (description, current price, market cap and price change percentage)

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


class SearchToken(BaseTool):
    name: str = "search_token"
    description: str = dedent(
        """
        Search token based on its symbol. It will return the ID of tokens with the largest market cap

        Args:
            token_symbol (str): Symbol of token to search
            retrieve_duplicate (bool): Set to True to retrieve all instances of tokens sharing the same symbol, indicating potential duplicates.
                By default, it is False, meaning only a single, most relevant token is retrieved unless duplication is explicitly requested.
        """
    )

    def _run(self, token_symbol: str, retrieve_duplicate: str):
        retrieve_all = retrieve_duplicate in ["true", "True"]
        response = get_coingecko().search.get(token_symbol)

        if len(response["coins"]) == 0:
            return f"No tokens found for search with symbol: {token_symbol}"

        tokens = [token["api_symbol"] for token in response["coins"]]
        return json.dumps(tokens if retrieve_all else tokens[0])


class GetAvailableCategories(BaseTool):
    name: str = "get_available_categories"
    description: str = dedent(
        """
        Retrieve all categories id
        """
    )

    def _run(self):
        categories = get_coingecko().categories.get_list()
        return json.dumps([category["category_id"] for category in categories])


class GetTokensBasedOnCategory(AutoTxTool):
    name: str = "get_tokens_based_on_category"
    description: str = dedent(
        f"""
        Retrieve all tokens with their respective information (symbol, market cap, price change percentages and total traded volume in the last 24 hours) from a given category

        Args:
            category (str): Category to retrieve tokens
            sort_by (str): Sort tokens by field. It can be: "volume_desc" | "volume_asc" | "market_cap_desc" | "market_cap_asc"
                "market_cap_desc" is the default
            limit (int): The number of tokens to return from the category
            price_change_percentage_interval (str): Interval of time in price change percentage.
                It can be: "1h" | "24h" | "7d" | "14d" | "30d" | "200d" | "1y".
                "24h" is the default
            network_name (str):  Possible values include: {SUPPORTED_NETWORKS_AS_STRING}.
                Use this parameter only if you require analysis for a specific network. Otherwise, pass an empty string
        """
    )

    def _run(
        self,
        category: str,
        sort_by: str,
        limit: int,
        price_change_percentage_interval: str,
        network_name: Optional[str],
    ):
        try:
            tokens_in_category = get_coingecko().coins.get_markets(
                vs_currency="usd",
                category=category,
                order=sort_by,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
                per_page=250,
            )
        except GeckoAPIException as e:
            if "Not Found" == e.error_message["error"]:
                raise Exception(
                    f"Category {category} not found. Check the available categories"
                )

        if network_name:
            tokens_in_category_map = {
                category["id"]: category for category in tokens_in_category
            }
            filtered_tokens_map = {
                token["id"]: token
                for token in get_tokens_and_filter_per_network(network_name)
            }
            tokens_in_category = [
                {
                    **tokens_in_category_map[token["id"]],
                    **filtered_tokens_map[token["id"]],
                }
                for token in tokens_in_category
                if token["id"] in filtered_tokens_map
            ]

            # If token is not in our token registry, we add it
            current_network = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(
                self.autotx.network.network
            )
            asked_network = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(
                EthereumNetwork[network_name]
            )
            if current_network == asked_network:
                for token_with_address in tokens_in_category:
                    token_symbol = token_with_address["symbol"].lower()
                    token_not_added = token_symbol not in self.autotx.network.tokens
                    if token_not_added:
                        self.autotx.network.tokens[token_symbol] = (
                            Web3.to_checksum_address(
                                token_with_address["platforms"][current_network]
                            )
                        )

        interval = (
            price_change_percentage_interval
            if price_change_percentage_interval
            else "24h"
        )
        price_change = f"price_change_percentage_{interval}"
        tokens = [
            {
                "symbol": token["symbol"],
                "market_cap": token["market_cap"],
                "total_volume_last_24h": token["total_volume"],
                price_change: token[price_change + "_in_currency"],
            }
            for token in tokens_in_category[:limit]
        ]

        return json.dumps(tokens)


class TokenExchanges(BaseTool):
    name: str = "get_exchanges_where_token_can_be_traded"
    description: str = dedent(
        """
        Retrieve exchanges name where token can be traded
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
            goal=f"Help users with real-time analytics and trend predictions",
            backstory="Designed to address the challenge of navigating the complex and fast-paced world of cryptocurrencies",
            tools=[
                GetTokenInformation(),
                SearchToken(),
                GetTokensBasedOnCategory(autotx),
                GetAvailableCategories(),
                TokenExchanges(),
            ],
        )


def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> ResearchTokensAgent:
        return ResearchTokensAgent(autotx)

    return agent_factory
