from web3 import Web3
from web3.types import TxParams, Wei

from autotx.utils.ethereum.eth_address import ETHAddress
from .constants import GAS_PRICE_MULTIPLIER
from .erc20_abi import ERC20_ABI

def build_transfer_erc20(web3: Web3, token_address: ETHAddress, to: ETHAddress, value: float) -> TxParams:
    erc20 = web3.eth.contract(address=token_address.hex, abi=ERC20_ABI)
    decimals = erc20.functions.decimals().call()
    tx: TxParams = erc20.functions.transfer(
        to.hex, int(value * 10**decimals)
    ).build_transaction(
        {
            "gas": None, # type: ignore
            "gasPrice": Wei(int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER))
        }
    )

    return tx
