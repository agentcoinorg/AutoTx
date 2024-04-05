from textwrap import dedent
from typing import Annotated, Callable
from autotx.AutoTx import AutoTx
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_eth import build_transfer_eth
from web3.constants import ADDRESS_ZERO
from autotx.autotx_autogen_agent import AutoTxAutogenAgent
from autotx.utils.ethereum.eth_address import ETHAddress
from autogen import AssistantAgent, UserProxyAgent, Agent

transfer_eth_info = {
    "name": "prepare_transfer_eth_transaction",
    "description": "Prepares a transfer transaction for given amount in decimals for ETH"
}
transfer_erc20_info = {
    "name": "prepare_transfer_erc20_token_transaction",
    "description": "Prepares a transfer transaction for given amount in decimals for given token"
}
get_eth_balance_info = {
    "name": "get_eth_balance",
    "description": "Check owner balance in ETH"
}
get_erc20_balance_info = {
    "name": "get_erc20_balance",
    "description": "Check owner balance in ERC20 token"
}

def build_agent_factory() -> Callable[[AutoTx, UserProxyAgent, dict], Agent]:
    def agent_factory(autotx: AutoTx, user_proxy: UserProxyAgent, llm_config: dict) -> AutoTxAutogenAgent:
        tokens = autotx.network.tokens

        agent = AssistantAgent(
            name="send-tokens",
            system_message=f"You are an AI assistant. Assist the user (address: {autotx.manager.address}) in their tasks by fetching balances and preparing transactions to send tokens.\n" + 
                dedent(
                    """
                    You are an expert in Ethereum tokens and can help users send tokens and check their balances.
                    You use the tools available to assist the user in their tasks. 
                    Your job is to only prepare the transactions and the user will take care of executing them.
                    NOTE: There is no reason to call get_erc20_balance after calling transfer as the transfers are only prepared and not executed. 
                    """
                ),
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
        )
    
        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=transfer_eth_info["name"],
            description=transfer_eth_info["description"]
        )
        def transfer_eth_tool(
            amount: Annotated[float, "Amount given by the user to transfer. The function will take care of converting the amount to needed decimals."],
            receiver: Annotated[str, "The receiver's address or ENS domain"]
        ) -> str:
            web3 = load_w3()
      
            receiver_addr = ETHAddress(receiver, web3)
        
            tx = build_transfer_eth(web3, ETHAddress(ADDRESS_ZERO, web3), receiver_addr, amount)
        
            prepared_tx = PreparedTx(f"Transfer {amount} ETH to {str(receiver_addr)}", tx)

            autotx.transactions.append(prepared_tx)
            
            return prepared_tx.summary
        
        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=transfer_erc20_info["name"],
            description=transfer_erc20_info["description"]
        )
        def transfer_erc20_token_tool(
            amount: Annotated[float, "Amount given by the user to transfer. The function will take care of converting the amount to needed decimals."],
            receiver: Annotated[str, "The receiver's address or ENS domain"],
            token: Annotated[str, "Symbol of token to transfer"]
        ) -> str:
            token_address = tokens[token.lower()]
            web3 = load_w3()
      
            receiver_addr = ETHAddress(receiver, web3)
        
            tx = build_transfer_erc20(web3, token_address, receiver_addr, amount)
        
            prepared_tx = PreparedTx(f"Transfer {amount} {token} to {str(receiver_addr)}", tx)
        
            autotx.transactions.append(prepared_tx)
        
            return prepared_tx.summary
        
        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=get_eth_balance_info["name"],
            description=get_eth_balance_info["description"]
        )
        def get_eth_balance_tool(
            owner: Annotated[str, "The owner's address or ENS domain"]
        ) -> float:
            web3 = load_w3()
            
            owner_addr = ETHAddress(owner, web3)

            eth_balance = web3.eth.get_balance(owner_addr.hex)

            return eth_balance / 10 ** 18

        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=get_erc20_balance_info["name"],
            description=get_erc20_balance_info["description"]
        )
        def get_erc20_balance_tool(
            token: Annotated[str, "Token symbol of erc20"],
            owner: Annotated[str, "The token owner's address or ENS domain"]
        ) -> float:
            web3 = load_w3()
            token_address = ETHAddress(tokens[token.lower()], web3)
            owner_addr = ETHAddress(owner, web3)
            
            return get_erc20_balance(web3, token_address, owner_addr)

        return AutoTxAutogenAgent(agent, tools=[
            f"{transfer_eth_info['name']}: {transfer_eth_info['description']}",
            f"{transfer_erc20_info['name']}: {transfer_erc20_info['description']}",
            f"{get_eth_balance_info['name']}: {get_eth_balance_info['description']}",
            f"{get_erc20_balance_info['name']}: {get_erc20_balance_info['description']}",
        ])

    return agent_factory
