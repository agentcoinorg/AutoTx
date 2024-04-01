import json
from textwrap import dedent
from typing import Callable
from crewai import Agent
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.utils.coingecko.api import CoingeckoApi
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
            token_id (str): Token ID expected by coingecko api
        """
    )

    def _run(self, token_id: str):
        endpoint = f"/coins/{token_id}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false"
        token_information = coingecko.request(endpoint=endpoint)
        return json.dumps(
            {
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
        get_categories = "/coins/categories/list"
        categories = coingecko.request(endpoint=get_categories)
        return json.dumps(categories)


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
        """
    )

    def _run(self, category: str, sort_by: str, limit: int):
        get_tokens_endpoint = f"/coins/markets?vs_currency=usd&category={category}&order={sort_by}&price_change_percentage=1h,24h,7d,14d,30d,200d,1y"
        tokens_in_category = coingecko.request(endpoint=get_tokens_endpoint)

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
                GetTokensBasedOnCategory(),
                GetAvailableCategories()
            ],
        )


def build_agent_factory(client: EthereumClient) -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> TokenResearchAgent:
        return TokenResearchAgent(autotx, client)

    return agent_factory
