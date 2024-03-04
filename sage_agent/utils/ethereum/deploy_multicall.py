import os
from eth_account import Account
from gnosis.eth import EthereumClient
from gnosis.eth.multicall import Multicall

from sage_agent.utils.ethereum import cache


def  deploy_multicall(client: EthereumClient, account: Account) -> str:
    if os.getenv("MULTICALL_ADDRESS"):
        return os.getenv("MULTICALL_ADDRESS")

    address = cache(lambda: deploy(client, account), "./.cache/multicall-address.txt")

    return address

def deploy(client: EthereumClient, account: Account) -> str:
    tx =  Multicall.deploy_contract(client, account) 

    if not tx.contract_address:
        raise ValueError("Multicall contract address is not set")
    
    client.w3.eth.wait_for_transaction_receipt(tx.tx_hash)

    print("Deployed Multicall to: ", tx.contract_address)

    return tx.contract_address