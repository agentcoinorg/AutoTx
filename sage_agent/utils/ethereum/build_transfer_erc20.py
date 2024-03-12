from web3 import Web3
from web3.types import TxParams
from .constants import GAS_PRICE_MULTIPLIER
from .mock_erc20 import MOCK_ERC20_ABI


def build_transfer_erc20(web3: Web3, token_address: str, to: str, value: float):
    token_address = web3.to_checksum_address(token_address)
    erc20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)
    decimals = erc20.functions.decimals().call()
    tx: TxParams = erc20.functions.transfer(
        to, int(value * 10**decimals)
    ).build_transaction(
        {"gas": None, "gasPrice": web3.eth.gas_price * GAS_PRICE_MULTIPLIER}
    )

    return tx
