
import json
from textwrap import dedent
from typing import Annotated, Callable, Optional, Union, cast
from web3 import Web3
from autotx.AutoTx import AutoTx
from gnosis.eth import EthereumNetworkNotSupported as ChainIdNotSupported
from coingecko import GeckoAPIException, CoinGeckoDemoClient

from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.constants import COINGECKO_API_KEY
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_AS_STRING, ChainId

name = "research-tokens"

system_message = lambda autotx: dedent(f"""
    You are an AI assistant that's an expert in Ethereum tokens. Assist the user in their task of researching tokens.
    ONLY focus on the token research aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks.
    NEVER ask the user questions.
    Retrieve token information, get token price, market cap, and price change percentage.
    BEFORE calling get_tokens_based_on_category always call get_available_categories to get the list of available categories.
    You MUST keep in mind the network the user is on and if the request is for a specific network, all networks, or the current network (it could be implied).
    If the user is interested in buying the tokens you're researching make sure you're searching them for his network.
    If searching for tokens to buy, make sure to:
    1. Get all the tokens you need (if fetching from multiple categories the tokens could overlap, so you might need to fetch more until you get the number you need)
    2. Calculate how much of each token to buy
    If a token does not have enough liquidity on the network, either:
    - Search for another token (if it is within the user's goal)
    - Or inform the user that the token is not available on the network (E.g. if the user's goal is to buy that specific token)
    If a user wants to research a specific number of tokens across categories, make sure to get the exact number of tokens without duplicates.
    If some tokens are not available, find alternatives and inform the user.
    """
)

description = dedent(
    f"""
    {name} is an AI assistant that's an expert in Ethereum tokens.
    The agent can also research, discuss, plan actions and advise the user.
    """
)

COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP = {
    ChainId.MAINNET: "ethereum",
    ChainId.OPTIMISM: "optimistic-ethereum",
    ChainId.POLYGON: "polygon-pos",
    ChainId.BASE_MAINNET: "base",
    ChainId.ARBITRUM_ONE: "arbitrum-one",
    ChainId.GNOSIS: "xdai",
}

def get_coingecko() -> CoinGeckoDemoClient:
    return CoinGeckoDemoClient(api_key=COINGECKO_API_KEY)


def get_tokens_and_filter_per_network(
    network_name: str,
) -> list[dict[str, Union[str, dict[str, str]]]]:
    network = ChainId[network_name] # type: ignore
    coingecko_network_key = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(network)
    if coingecko_network_key == None:
        raise ChainIdNotSupported(f"Network {network_name} not supported")

    token_list_with_addresses = get_coingecko().coins.get_list(include_platform=True)
    return [
        token
        for token in token_list_with_addresses
        if coingecko_network_key in token["platforms"]
    ]

def filter_token_list_by_network(tokens: list[dict[str, str]], network_name: str) -> list[dict[str, Union[str, dict[str, str]]]]:
    tokens_in_category_map = {category["id"]: category for category in tokens}
    filtered_tokens_map = {
        token["id"]: token for token in get_tokens_and_filter_per_network(network_name)
    }

    return [
        {
            **tokens_in_category_map[token["id"]],
            **filtered_tokens_map[token["id"]],
        }
        for token in tokens
        if token["id"] in filtered_tokens_map
    ]

def add_tokens_address_if_not_in_registry(
    tokens_in_category: list[dict[str, Union[str, dict[str, str]]]],
    tokens: dict[str, str],
    current_network: str,
) -> None:
    for token_with_address in tokens_in_category:
        token_symbol = cast(str, token_with_address["symbol"]).lower()
        token_not_added = token_symbol not in tokens
        if token_not_added:
            platforms = cast(dict[str, str], token_with_address["platforms"]) 
            tokens[token_symbol] = Web3.to_checksum_address(
                platforms[current_network]
            )

class GetTokenInformationTool(AutoTxTool):
    name: str = "get_token_information"
    description: str = dedent(
        """
        Retrieve token information (description, current price, market cap and price change percentage)
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable[[str], str]:
        def run(
            token_id: Annotated[str, "ID of token"]
        ) -> str:
            autotx.notify_user(f"Fetching token information for {token_id}")
           
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

        return run

class SearchTokenTool(AutoTxTool):
    name: str = "search_token"
    description: str = "Search token based on its symbol. It will return the ID of tokens with the largest market cap"

    def build_tool(self, autotx: AutoTx) -> Callable[[str, bool], str]:
        def run(
            token_symbol: Annotated[str, "Symbol of token to search"],
            retrieve_duplicate: Annotated[bool, "Set to true to retrieve all instances of tokens sharing the same symbol, indicating potential duplicates. By default, it is False, meaning only a single, most relevant token is retrieved unless duplication is explicitly requested."]
        ) -> str:
            autotx.notify_user(f"Searching for token with symbol: {token_symbol}")

            response = get_coingecko().search.get(token_symbol)

            if len(response["coins"]) == 0:
                return f"No tokens found for search with symbol: {token_symbol}"

            tokens = [token["api_symbol"] for token in response["coins"]]
            return json.dumps(tokens if retrieve_duplicate else tokens[0])

        return run

class GetAvailableCategoriesTool(AutoTxTool):
    name: str = "get_available_categories"
    description: str = "Retrieve all available category ids of tokens"

    def build_tool(self, autotx: AutoTx) -> Callable[[], str]:
        def run() -> str:
            autotx.notify_user("Fetching available token categories")

            categories = get_coingecko().categories.get_list()
            return json.dumps([category["category_id"] for category in categories])
        
        return run
    
class GetTokensBasedOnCategoryTool(AutoTxTool):
    name: str = "get_tokens_based_on_category"
    description: str = "Retrieve all tokens with their respective information (symbol, market cap, price change percentages and total traded volume in the last 24 hours) from a given category"

    def build_tool(self, autotx: AutoTx) -> Callable[[str, str, int, str, Optional[str]], str]:
        def run(
            category: Annotated[str, "Category to retrieve tokens"],
            sort_by: Annotated[str, "Sort tokens by field. It can be: 'volume_desc' | 'volume_asc' | 'market_cap_desc' | 'market_cap_asc'. 'market_cap_desc' is the default"],
            limit: Annotated[int, "The number of tokens to return from the category"],
            price_change_percentage_interval: Annotated[str, "Interval of time in price change percentage. It can be: '1h' | '24h' | '7d' | '14d' | '30d' | '200d' | '1y'. '24h' is the default"],
            network_name: Annotated[Optional[str], f"Possible values include: {SUPPORTED_NETWORKS_AS_STRING}. Use this parameter only if you require analysis for a specific network. Otherwise, pass an empty string"]
        ) -> str:
            autotx.notify_user(f"Fetching tokens from category: {category}")

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
                tokens_in_category = filter_token_list_by_network(
                    tokens_in_category, network_name
                )

                current_network = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(
                    autotx.network.chain_id
                )
                asked_network = COINGECKO_NETWORKS_TO_SUPPORTED_NETWORKS_MAP.get(
                    ChainId[network_name] # type: ignore
                )
                if current_network == asked_network:
                    add_tokens_address_if_not_in_registry(
                        tokens_in_category, autotx.network.tokens, cast(str, current_network)
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

        return run

class ResearchTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    description = description
    tools = [
        GetTokenInformationTool(),
        SearchTokenTool(),
        GetAvailableCategoriesTool(),
        GetTokensBasedOnCategoryTool(),
    ]
