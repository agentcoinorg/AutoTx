import os
from gnosis.eth import EthereumClient
from gnosis.eth.multicall import Multicall
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes

from autotx.utils.ethereum.eth_address import ETHAddress

from .cache import cache

def deploy_multicall(client: EthereumClient, account: LocalAccount) -> ETHAddress:
    multicall_address = os.getenv("MULTICALL_ADDRESS") 
    if multicall_address:
        return ETHAddress(multicall_address)
    multicall_address = deploy(client, account)
    cache.write("multicall-address.txt", multicall_address)
    return ETHAddress(multicall_address)

def deploy(client: EthereumClient, account: LocalAccount) -> str:
    tx =  Multicall.deploy_contract(client, account) 

    if not tx.contract_address:
        raise ValueError("Multicall contract address is not set")
    
    client.w3.eth.wait_for_transaction_receipt(HexBytes(tx.tx_hash))

    print("Deployed Multicall to: ", tx.contract_address)

    return tx.contract_address