from web3 import Web3
from web3.types import TxParams
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.mock_erc20 import MOCK_ERC20_ABI

def build_approve_erc20(web3: Web3, token_address: ETHAddress, spender: ETHAddress, value: float):
    erc20 = web3.eth.contract(address=token_address.hex, abi=MOCK_ERC20_ABI)
    decimals = erc20.functions.decimals().call()

    tx: TxParams = erc20.functions.approve(spender.hex, int(value * 10 ** decimals)).build_transaction()

    return tx
