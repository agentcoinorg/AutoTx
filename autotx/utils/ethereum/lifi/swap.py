from decimal import Decimal
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum.constants import GAS_PRICE_MULTIPLIER, NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.erc20_abi import ERC20_ABI
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_native_token_symbol import get_native_token_symbol
from autotx.utils.ethereum.lifi import Lifi
from autotx.utils.ethereum.networks import ChainId
from gnosis.eth import EthereumClient
from web3.types import TxParams, Wei

SLIPPAGE = 0.01 # 1%

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

    if not is_exact_input:
        token_in_price_in_usd = Lifi.get_token_price(token_in_address, chain)
        token_out_price_in_usd = Lifi.get_token_price(token_out_address, chain)
        amount_token_to_buy = (token_out_price_in_usd * amount) / token_in_price_in_usd
        amount_in_integer = int(amount_token_to_buy * (10**decimals))
        # add slippage plus 0.05% to ensure we get the expected amount
        amount_in_integer = int(amount_in_integer * 0.005 + amount_in_integer)

    quote = Lifi.get_quote(
        token_in_address, token_out_address, amount_in_integer, _from, chain, SLIPPAGE
    )
    transactions: list[PreparedTx] = []

    native_token_symbol = get_native_token_symbol(chain)
    token_in_symbol = native_token_symbol if token_in_is_native else token_in.functions.symbol().call()
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
                    f"Approve {amount_in_integer / 10 ** decimals} {token_in_symbol} to {quote['toolDetails']['name']}",
                    tx,
                )
            )

    transaction = TxParams(
        {
            "to": quote["transactionRequest"]["to"],
            "from": quote["transactionRequest"]["from"],
            "data": quote["transactionRequest"]["data"],
            "gasPrice": quote["transactionRequest"]["gasPrice"],
            "gas": quote["transactionRequest"]["gasLimit"],
            "value": Wei(int(quote["transactionRequest"]["value"], 0)),
        }
    )
    token_out_is_native = token_out_address.hex == NATIVE_TOKEN_ADDRESS
    token_out = ethereum_client.w3.eth.contract(
        address=token_out_address.hex, abi=ERC20_ABI
    )
    token_out_symbol = native_token_symbol if token_out_is_native else token_out.functions.symbol().call()
    token_out_decimals = 18 if token_out_is_native else token_out.functions.decimals().call()
    transactions.append(PreparedTx(f"Swap {amount_in_integer / 10 ** decimals} {token_in_symbol} for at least {int(quote['estimate']['toAmountMin']) / 10 ** token_out_decimals} {token_out_symbol}", transaction))
    return transactions
