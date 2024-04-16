from decimal import Decimal
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum.constants import GAS_PRICE_MULTIPLIER, NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.erc20_abi import ERC20_ABI
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi import Lifi
from autotx.utils.ethereum.networks import ChainId
from gnosis.eth import EthereumClient
from web3.types import TxParams, Wei


def build_swap_transaction(
    ethereum_client: EthereumClient,
    amount: Decimal,
    token_in_address: ETHAddress,
    token_out_address: ETHAddress,
    _from: ETHAddress,
    is_exact_input: bool,
    chain: ChainId,
) -> list[PreparedTx]:
    token_in_is_native = token_in_address.hex == NATIVE_TOKEN_ADDRESS
    token_in = ethereum_client.w3.eth.contract(
        address=token_in_address.hex, abi=ERC20_ABI
    )
    decimals = 18 if token_in_is_native else token_in.functions.decimals().call()
    amount_in_integer = int(amount * (10**decimals))
    quote = Lifi.get_quote(
        token_in_address, token_out_address, amount_in_integer, _from, chain
    )

    transactions: list[PreparedTx] = []

    if not token_in_is_native:
        approval_address = quote["estimate"]["approvalAddress"]
        allowance = token_in.functions.allowance(_from.hex, approval_address).call()
        if allowance < amount_in_integer:
            tx = token_in.functions.approve(
                approval_address, amount_in_integer
            ).build_transaction(
                {
                    "from": _from.hex,
                    "gasPrice": Wei(int(ethereum_client.w3.eth.gas_price * GAS_PRICE_MULTIPLIER)),
                }
            )
            transactions.append(
                PreparedTx(
                    f"Approve",
                    tx,
                )
            )

    transaction = TxParams(
        {
            "to": quote["transactionRequest"]["to"],
            "from": quote["transactionRequest"]["from"],
            "data": quote["transactionRequest"]["data"],
            "gasPrice": quote["transactionRequest"]["gasPrice"],
            "gasLimit": quote["transactionRequest"]["gasLimit"],
            "value": int(quote["transactionRequest"]["value"], 0),
        }
    )
    transactions.append(PreparedTx("", transaction))
    return transactions
