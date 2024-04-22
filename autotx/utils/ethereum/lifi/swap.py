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
from autotx.utils.ethereum.lifi import Lifi, TokenNotSupported
from autotx.utils.ethereum.networks import ChainId
from gnosis.eth import EthereumClient
from web3.types import TxParams, Wei

SLIPPAGE = 0.005  # 0.5%


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
    token_in_symbol: str,
    token_out_address: ETHAddress,
    token_out_decimals: int,
    token_out_symbol: str,
    chain: ChainId,
    expected_amount: Decimal,
    amount_is_output: bool,
    from_address: ETHAddress,
) -> QuoteInformation:
    quote: dict[str, Any] | None = None
    try:
        if amount_is_output:
            quote = Lifi.get_quote_to_amount(
                token_in_address,
                token_out_address,
                int(expected_amount * (10**token_out_decimals)),
                from_address,
                chain,
                SLIPPAGE,
            )
            amount_in_integer = int(quote["estimate"]["fromAmount"])

        else:
            amount_in_integer = int(expected_amount * (10**token_in_decimals))
            quote = Lifi.get_quote_from_amount(
                token_in_address,
                token_out_address,
                amount_in_integer,
                from_address,
                chain,
                SLIPPAGE,
            )
    except TokenNotSupported as e:
        if e.token_address.lower() == token_in_address.hex.lower():
            raise Exception(
                f"Token {token_in_symbol} is not supported. Please try another one"
            )
        if e.token_address.lower() == token_out_address.hex.lower():
            raise Exception(
                f"Token {token_out_symbol} is not supported. Please try another one"
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
) -> list[PreparedTx]:
    native_token_symbol = get_native_token_symbol(chain)
    token_in_is_native = token_in_address.hex == NATIVE_TOKEN_ADDRESS
    token_in = ethereum_client.w3.eth.contract(
        address=token_in_address.hex, abi=ERC20_ABI
    )
    token_in_symbol = (
        native_token_symbol
        if token_in_is_native
        else token_in.functions.symbol().call()
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

    token_out_symbol = (
        native_token_symbol
        if token_out_is_native
        else token_out.functions.symbol().call()
    )
    quote = get_quote(
        token_in_address,
        token_in_decimals,
        token_in_symbol,
        token_out_address,
        token_out_decimals,
        token_out_symbol,
        chain,
        amount,
        not is_exact_input,
        _from,
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
                    f"Approve {Decimal(quote.amount_in / 10 ** token_in_decimals)} {token_in_symbol} to {quote.exchange_name}",
                    tx,
                )
            )
    transactions.append(
        PreparedTx(
            f"Swap {Decimal(quote.amount_in / 10 ** token_in_decimals)} {token_in_symbol} for at least {Decimal(int(quote.to_amount_min) / 10 ** token_out_decimals)} {token_out_symbol}",
            quote.transaction,
        )
    )
    return transactions
