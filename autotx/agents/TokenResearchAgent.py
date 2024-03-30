import json
from textwrap import dedent
from typing import Callable
from crewai import Agent
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.coingecko.api import CoingeckoApi
from autotx.utils.ethereum.eth_address import ETHAddress
from gnosis.eth import EthereumClient
from crewai_tools import BaseTool

coingecko = CoingeckoApi()


class TokenSymbolToTokenId(BaseTool):
    name: str = "token_symbol_to_token_id"
    description: str = dedent(
        """
        Fetch tokens list from coingecko,

        Args:
            token_symbol (list[str]): Token symbols to map token id from coingecko
        Returns:
            token_ids (list[str]): Token IDs of coingecko to get information from tokens
        """
    )

    def _run(self, token_symbols: list[str]):
        endpoint = "/coins/list"
        token_list = coingecko.request(endpoint=endpoint)
        return json.dumps([item["id"] for item in token_list if item["symbol"] in token_symbols])


class GetTokenInformation(BaseTool):
    name: str = "get_token_information"
    description: str = dedent(
        """
        Retrieve token information (current price, market cap and price change percentage)

        Args:
            token_id (str): Token ID expected by coingecko api
        """
    )

    def _run(self, token_id: str):
        endpoint = f"/coins/{token_id}?localization=false"
        token_information = coingecko.request(endpoint=endpoint)
        return json.dumps({
            "current_price": token_information["market_data"]["current_price"]["usd"],
            "market_cap": token_information["market_cap"]["usd"],
            "price_change_percentage_24h": token_information["market_data"][
                "price_change_percentage_24h"
            ],
        })


# class GetTokensListWithMarketData(AutoTxTool):
#     name: str = "get_tokens_list_with_market_data"
#     description: str = dedent(
#         """
#         Retrieve token information

#         Args:
#             token_id (str): Token ID expected by coingecko api to retrieve the historical price of token
#         """
#     )

#     def _run(self, token_id: str):
#         pass


class GetTokensBasedOnCategory(AutoTxTool):
    name: str = "get_tokens_based_on_category"
    description: str = dedent(
        """
        Retrieve all tokens from a given category key using coingecko api

        Args:
            category_key (str): Category expected by coingecko api to retrieve needed tokens
        """
    )

    def _run(self, category_key: str):
        pass


class CheckAvailableCategories(AutoTxTool):
    name: str = "check_available_categories"
    description: str = dedent(
        """
        Get available categories from coingecko
        """
    )

    def _run(self, category_desired: str):
        pass


class TokenResearchAgent(AutoTxAgent):
    def __init__(self):
        super().__init__(
            name="token-researcher",
            role="Highly specialized AI assistant with expertise in cryptocurrency analysis and investment strategies",
            goal="Empower users with real-time analytics, trend predictions, and personalized investment opportunities.",
            backstory="Designed to address the challenge of navigating the complex and fast-paced world of cryptocurrency investments.",
            tools=[
                GetTokenInformation(),
                TokenSymbolToTokenId(),
                # GetTokensBasedOnCategory(),
                # CheckAvailableCategories(),
            ],
        )


def build_agent_factory(client: EthereumClient) -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> TokenResearchAgent:
        return TokenResearchAgent(autotx, client)

    return agent_factory
