import json
import os
from textwrap import dedent
from typing import Callable
from crewai import Agent
from web3 import Web3
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from crewai_tools import BaseTool
import coingecko

from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.ethereum.constants import SUPPORTED_NETWORKS


def get_coingecko():
    return coingecko.CoinGeckoDemoClient(api_key=os.getenv("COINGECKO_API_KEY"))


COINGECKO_NETWORK_IDS = [
    "ethereum",
    "avalanche",
    "optimistic-ethereum",
    "arbitrum-one",
    "base",
    "polygon-pos",
    "xdai",
]

COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP = {
    "ethereum": SUPPORTED_NETWORKS.get(1),
    "optimistic-ethereum": SUPPORTED_NETWORKS.get(10),
    "polygon-pos": SUPPORTED_NETWORKS.get(137),
    "base": SUPPORTED_NETWORKS.get(8453),
    "arbitrum-one": SUPPORTED_NETWORKS.get(42161),
    "xdai": SUPPORTED_NETWORKS.get(100),
}


class TokenSymbolToTokenId(BaseTool):
    name: str = "token_symbol_to_token_id"
    description: str = dedent(
        """
        Fetch token list and returns token ID based on symbol given

        Args:
            token_symbol (list[str]): Symbol of tokens
        """
    )

    def _run(self, token_symbols: list[str]):
        token_list = get_coingecko().coins.get_list()
        token_symbols_in_lower = [symbol.lower() for symbol in token_symbols]
        return json.dumps(
            [
                item["id"]
                for item in token_list
                if item["symbol"] in token_symbols_in_lower
            ]
        )


class GetTokenInformation(AutoTxTool):
    name: str = "get_token_information"
    description: str = dedent(
        """
        Retrieve token information (current price, market cap and price change percentage).
        If the token is not supported by our toolset, the function will explicitly return a message saying that

        Args:
            token_id (str): ID of token
        """
    )

    def __init__(self, autotx: AutoTx):
        super().__init__(autotx)

    def _run(self, token_id: str):
        token_information = get_coingecko().coins.get_id(
            id=token_id,
            localization=False,
            tickers=False,
            community_data=False,
            sparkline=False,
        )

        # 1- Get token symbol & addresses
        # 2- Map network of address to supported network names in constants.py
        # 3- Update token dictionary with addresses fetched from
        token_symbol = token_information["symbol"]
        self.autotx.network.network.name
        if not token_symbol in self.autotx.network.tokens:
            return f"Token {token_symbol} is not supported"

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


class GetTokensBasedOnCategory(AutoTxTool):
    name: str = "get_tokens_based_on_category"
    description: str = dedent(
        """
        Retrieve all tokens from a given category

        Args:
            category (str): Category to retrieve tokens
            sort_by (str): Sort tokens by field. It can be: "volume_desc" | "volume_asc" | "market_cap_desc" | "market_cap_asc"
                "market_cap_desc" should be the default if none is defined
            limit (int): The number of tokens to return from the category
        """
    )

    def __init__(self, autotx: AutoTx):
        super().__init__(autotx)

    def _run(self, category: str, sort_by: str, limit: int):
        tokens_in_category = get_coingecko().coins.get_markets(
            vs_currency="usd",
            category=category,
            order=sort_by,
            price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
        )

        tokens_with_addresses = get_coingecko().coins.get_list(include_platform=True)

        supported_tokens = []
        for token in tokens_in_category:
            token_with_address = next(
                (t for t in tokens_with_addresses if t["id"] == token["id"]), None
            )
            if not tokens_with_addresses:
                continue

            for platform in token_with_address["platforms"]:
                if platform in COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP:
                    # network = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP[platform]
                    COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP[platform].tokens[
                        token["symbol"].lower()
                    ] = Web3.to_checksum_address(
                        token_with_address["platforms"][platform]
                    )

            # self.autotx.

        # supported_tokens = [token for token in tokens_in_category if ]

        tokens = [
            {
                "id": token["id"],
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
            for token in tokens_in_category[:limit]
        ]

        return json.dumps(tokens)


# class CheckTokenIsSupported(AutoTxTool):
#     name: str = "check_token_is_supported"
#     description: str = dedent(
#         """
#         Check if token with given symbol is supported
#         Args:
#             token_symbol (str): Symbol of token
#         """
#     )
#     def __init__(self, autotx: AutoTx):
#         super().__init__(autotx)

#     def _run(self, token_symbol: str) -> str:
#         return token_symbol in self.autotx.network.tokens


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


class TokenResearchAgent(AutoTxAgent):
    def __init__(self, autotx: AutoTx):
        if os.getenv("COINGECKO_API_KEY") == None:
            raise "You must add a value to COINGECKO_API_KEY key in .env file"

        super().__init__(
            name="token-researcher",
            role="Highly specialized AI assistant with expertise in researching cryptocurrencies and analyzing the market",
            goal="Empower users with real-time analytics and trend predictions",
            backstory="Designed to address the challenge of navigating the complex and fast-paced world of cryptocurrencies",
            tools=[
                GetTokenInformation(autotx),
                TokenSymbolToTokenId(),
                GetTokensBasedOnCategory(autotx),
                GetAvailableCategories(),
                TokenExchanges(),
                # CheckTokenIsSupported(autotx)
            ],
        )


def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> TokenResearchAgent:
        return TokenResearchAgent(autotx)

    return agent_factory
