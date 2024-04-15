from decimal import Decimal
from autotx.utils.ethereum.eth_address import ETHAddress
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction


def swap(
    client: EthereumClient,
    user: LocalAccount,
    amount: float,
    from_token: ETHAddress,
    to_token: ETHAddress,
) -> None:
    txs = build_swap_transaction(
        client, Decimal(amount), from_token.hex, to_token.hex, user.address, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(  # type: ignore
            {
                **tx.tx,
                "nonce": client.w3.eth.get_transaction_count(user.address),
                "gas": 200000,
            }
        )

        hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = client.w3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction #{i} failed ")
            break
