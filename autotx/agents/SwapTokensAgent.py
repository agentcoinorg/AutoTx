from textwrap import dedent
from typing import Annotated, Callable
from autogen import AssistantAgent, UserProxyAgent, Agent
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.uniswap.swap import SUPPORTED_UNISWAP_V3_NETWORKS, build_swap_transaction
from gnosis.eth import EthereumNetworkNotSupported as ChainIdNotSupported

def get_tokens_address(token_in: str, token_out: str, network_info: NetworkInfo):
    token_in = token_in.lower()
    token_out = token_out.lower()

    if not network_info.chain_id in SUPPORTED_UNISWAP_V3_NETWORKS:
        raise ChainIdNotSupported(
            f"Network {network_info.chain_id.name} not supported for swap"
        )

    if token_in not in network_info.tokens:
        raise Exception(f"Token {token_in} is not supported")

    if token_out not in network_info.tokens:
        raise Exception(f"Token {token_out} is not supported")

    return (network_info.tokens[token_in], network_info.tokens[token_out])

swap_tool_info = {
    "name": "swap",
    "description": "Prepares a swap transaction for given amount in decimals for given token. Swap should only include the amount for one of the tokens, the other token amount will be calculated automatically."
}

def build_agent_factory() -> Callable[[AutoTx, UserProxyAgent, dict], Agent]:
    def agent_factory(autotx: AutoTx, user_proxy: UserProxyAgent, llm_config: dict) -> AutoTxAgent:
        agent = AssistantAgent(
            name="swap-tokens",
            system_message=dedent(f"""
                You are an expert at buying and selling tokens. Assist the user (address: {autotx.manager.address}) in their task of swapping tokens.
                You use the tools available to assist the user in their tasks.
                Perform token swaps, manage liquidity, and query pool statistics on the Uniswap protocol
                An autonomous agent skilled in Ethereum blockchain interactions, specifically tailored for the Uniswap V3 protocol.
                Note a balance of a token is not required to perform a swap, if there is an earlier prepared transaction that will provide the token.
                Examples:
                {{
                    "token_to_sell": "5 ETH",
                    "token_to_buy": "USDC"
                }} // Prepares a swap transaction to sell 5 ETH and buy USDC

                {{
                    "token_to_sell": "ETH",
                    "token_to_buy": "5 USDC"
                }} // Prepares a swap transaction to sell ETH and buy 5 USDC

                Invalid Example:
                {{
                    "token_to_sell": "5 ETH",
                    "token_to_buy": "5 USDC"
                }} // Invalid input. Only one token amount should be provided, not both.
                """
            ),
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
        )
    
        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=swap_tool_info["name"],
            description=swap_tool_info["description"]
        )
        def swap_tool(
            token_to_sell: Annotated[str, "Token to sell. E.g. '10 USDC' or just 'USDC'"],
            token_to_buy: Annotated[str, "Token to buy. E.g. '10 USDC' or just 'USDC'"],
        ) -> str:
            sell_parts = token_to_sell.split(" ")
            buy_parts = token_to_buy.split(" ")

            if len(sell_parts) == 2 and len(buy_parts) == 2:
                return "Invalid input. Only one token amount should be provided. IMPORTANT: Take another look at the user's goal, and try again."
            
            if len(sell_parts) < 2 and len(buy_parts) < 2:
                return "Invalid input. Token amount is missing.\n"

            token_symbol_to_sell = sell_parts[1] if len(sell_parts) == 2 else sell_parts[0]
            token_symbol_to_buy = buy_parts[1] if len(buy_parts) == 2 else buy_parts[0]

            exact_amount = sell_parts[0] if len(sell_parts) == 2 else buy_parts[0]
            amount_symbol = token_symbol_to_sell if len(sell_parts) == 2 else token_symbol_to_buy

            token_in = token_symbol_to_sell.lower()
            token_out = token_symbol_to_buy.lower()
            is_exact_input = True if amount_symbol == token_symbol_to_sell else False

            (token_in_address, token_out_address) = get_tokens_address(
                token_in, token_out, autotx.network
            )

            swap_transactions = build_swap_transaction(
                autotx.manager.client,
                float(exact_amount),
                token_in_address,
                token_out_address,
                autotx.manager.address.hex,
                is_exact_input,
            )
            autotx.transactions.extend(swap_transactions)

            token_in_amount = f"{exact_amount} " if is_exact_input else ""
            token_out_amount = f"{exact_amount} " if not is_exact_input else ""

            print(f"Prepared transaction: Buy {token_out_amount}{token_out} with {token_in_amount}{token_in}")

            return f"Transaction to buy {token_out_amount}{token_out} with {token_in_amount}{token_in} has been prepared"

        return AutoTxAgent(agent, tools=[
            f"{swap_tool_info['name']}: {swap_tool_info['description']}"
        ])

    return agent_factory
