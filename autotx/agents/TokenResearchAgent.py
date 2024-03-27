from textwrap import dedent
from typing import Callable
from crewai import Agent
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.coingecko.api import CoingeckoApi
from autotx.utils.ethereum.eth_address import ETHAddress
from gnosis.eth import EthereumClient

coingecko = CoingeckoApi()


class TokenHistoricalPrice(AutoTxTool):
    name: str = "token_historical_price"
    description: str = dedent(
        """
        Retrieve token historical price using coingecko api

        Args:
            token_id (str): Token ID expected by coingecko api to retrieve the historical price of token
        """
    )

    def _run(self, token_id: str):
        pass


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
                TokenHistoricalPrice(),
                GetTokensBasedOnCategory(),
                CheckAvailableCategories(),
            ],
        )


def build_agent_factory(client: EthereumClient) -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> TokenResearchAgent:
        return TokenResearchAgent(autotx, client)

    return agent_factory
