from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum.constants import GAS_PRICE_MULTIPLIER, NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.erc20_abi import ERC20_ABI
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_native_token_symbol import (
    get_native_token_symbol,
)
from autotx.utils.ethereum.lifi import Lifi
from autotx.utils.ethereum.networks import ChainId
from gnosis.eth import EthereumClient
from web3.types import TxParams, Wei

SLIPPAGE = 0.01  # 1%


@dataclass
class QuoteInformation:
    approval_address: str
    amount_in: int
    to_amount_min: int
    transaction: TxParams
    exchange_name: str


def get_quote(
    token_in_address: ETHAddress,
    token_in_decimals: int,
    token_out_address: ETHAddress,
    token_out_decimals: int,
    chain: ChainId,
    expected_amount: Decimal,
    amount_is_output: bool,
    from_address: ETHAddress,
    strict_output: bool,
) -> QuoteInformation:
    quote: dict[str, Any] | None = None
    if amount_is_output:
        token_in_price_in_usd = Lifi.get_token_price(token_in_address, chain)
        token_out_price_in_usd = Lifi.get_token_price(token_out_address, chain)
        amount_token_to_buy = (
            token_out_price_in_usd * expected_amount
        ) / token_in_price_in_usd
        amount_in_integer = int(amount_token_to_buy * (10**token_in_decimals))
        quote = Lifi.get_quote(
            token_in_address,
            token_out_address,
            amount_in_integer,
            from_address,
            chain,
            SLIPPAGE,
        )
        expected_amount_in_integer = int(expected_amount * (10**token_out_decimals))
        to_amount_min = int(quote["estimate"]["toAmountMin"])

        if strict_output:
            # The accepted max amount is expected amount + the 1% of the expected amount
            accepted_max_amount_in_integer = expected_amount_in_integer + (
                expected_amount_in_integer * 0.01
            )
            retries = 0
            while True:
                if retries == 4:
                    break
                """
                if to_amount_min is in an accepted range, we're good to do the swap
                the accepted range is:
                   - to_amount_min is equal or greater than the expected amount
                   - to_amount_min is equal or less than the accepted max amount
                """
                if (
                    to_amount_min >= expected_amount_in_integer
                    and to_amount_min <= accepted_max_amount_in_integer
                ):
                    break

                if to_amount_min < accepted_max_amount_in_integer:
                    surplus = (expected_amount_in_integer / to_amount_min) - 1
                    amount_in_integer = int(
                        amount_in_integer + (surplus * amount_in_integer)
                    )
                else:
                    shortage_percentage = 1 - (
                        to_amount_min / expected_amount_in_integer
                    )
                    amount_in_integer = int(
                        amount_in_integer + (shortage_percentage * amount_in_integer)
                    )

                quote = Lifi.get_quote(
                    token_in_address,
                    token_out_address,
                    amount_in_integer,
                    from_address,
                    chain,
                    SLIPPAGE,
                )

                to_amount_min = int(quote["estimate"]["toAmountMin"])
                retries += 1
    else:
        amount_in_integer = int(expected_amount * (10**token_in_decimals))
        quote = Lifi.get_quote(
            token_in_address,
            token_out_address,
            amount_in_integer,
            from_address,
            chain,
            SLIPPAGE,
        )

    if not quote:
        raise Exception("Quote has not been fetched")

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
    return QuoteInformation(
        quote["estimate"]["approvalAddress"],
        amount_in_integer,
        int(quote["estimate"]["toAmountMin"]),
        transaction,
        quote["toolDetails"]["name"],
    )


def build_swap_transaction(
    ethereum_client: EthereumClient,
    amount: Decimal,
    token_in_address: ETHAddress,
    token_out_address: ETHAddress,
    _from: ETHAddress,
    is_exact_input: bool,
    chain: ChainId,
    strict_output: bool = True,
) -> list[PreparedTx]:
    token_in_is_native = token_in_address.hex == NATIVE_TOKEN_ADDRESS
    token_in = ethereum_client.w3.eth.contract(
        address=token_in_address.hex, abi=ERC20_ABI
    )

    token_in_decimals = (
        18 if token_in_is_native else token_in.functions.decimals().call()
    )

    token_out_is_native = token_out_address.hex == NATIVE_TOKEN_ADDRESS
    token_out = ethereum_client.w3.eth.contract(
        address=token_out_address.hex, abi=ERC20_ABI
    )
    token_out_decimals = (
        18 if token_out_is_native else token_out.functions.decimals().call()
    )
    quote = get_quote(
        token_in_address,
        token_in_decimals,
        token_out_address,
        token_out_decimals,
        chain,
        amount,
        not is_exact_input,
        _from,
        strict_output,
    )

    native_token_symbol = get_native_token_symbol(chain)
    token_in_symbol = (
        native_token_symbol
        if token_in_is_native
        else token_in.functions.symbol().call()
    )
    transactions: list[PreparedTx] = []
    if not token_in_is_native:
        approval_address = quote.approval_address
        allowance = token_in.functions.allowance(_from.hex, approval_address).call()
        if allowance < quote.amount_in:
            tx = token_in.functions.approve(
                approval_address, quote.amount_in
            ).build_transaction(
                {
                    "from": _from.hex,
                    "gasPrice": Wei(
                        int(ethereum_client.w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
                    ),
                }
            )
            transactions.append(
                PreparedTx(
                    f"Approve {quote.amount_in / 10 ** token_in_decimals} {token_in_symbol} to {quote.exchange_name}",
                    tx,
                )
            )

    token_out_symbol = (
        native_token_symbol
        if token_out_is_native
        else token_out.functions.symbol().call()
    )
    transactions.append(
        PreparedTx(
            f"Swap {quote.amount_in / 10 ** token_in_decimals} {token_in_symbol} for at least {int(quote.to_amount_min) / 10 ** token_out_decimals} {token_out_symbol}",
            quote.transaction,
        )
    )
    return transactions
