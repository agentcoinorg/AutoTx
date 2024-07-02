from decimal import Decimal
from typing import cast
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.types import TxParams

from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import ChainId


def swap(
    web3: Web3,
    user: LocalAccount,
    amount: float,
    from_token: ETHAddress,
    to_token: ETHAddress,
    chain: ChainId,
) -> None:
    txs = build_swap_transaction(
        web3,
        Decimal(str(amount)),
        from_token,
        to_token,
        ETHAddress(user.address),
        False,
        chain
    )

    for tx in txs:
        del tx.params["gas"]
        gas = web3.eth.estimate_gas(cast(TxParams, tx.params))
        tx.params.update({"gas": gas})

        transaction = user.sign_transaction(  # type: ignore
            {
                **tx.params,
                "nonce": web3.eth.get_transaction_count(user.address),
            }
        )

        hash = web3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = web3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction to swap {from_token.hex} to {amount} {to_token.hex} failed")
