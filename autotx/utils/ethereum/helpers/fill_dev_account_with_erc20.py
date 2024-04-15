from autotx.utils.ethereum import transfer_erc20
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import NetworkInfo
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction


def fill_dev_account_with_erc20(
    client: EthereumClient,
    dev_account: LocalAccount,
    safe_address: ETHAddress,
    network_info: NetworkInfo,
):
    tokens_to_transfer = {"usdc": 3500, "dai": 3500, "wbtc": 0.1}
    eth_address = ETHAddress(network_info.tokens["eth"], client.w3)
    for token in network_info.tokens:
        if token in tokens_to_transfer:
            token_address = ETHAddress(network_info.tokens[token], client.w3)
            amount = tokens_to_transfer[token]
            swap(
                client,
                dev_account,
                tokens_to_transfer[token],
                eth_address,
                ETHAddress(network_info.tokens[token], client.w3),
            )
            transfer_erc20(client.w3, token_address, dev_account, safe_address, amount)


def swap(
    client: EthereumClient,
    user: LocalAccount,
    amount: float,
    from_token: ETHAddress,
    to_token: ETHAddress,
):
    txs = build_swap_transaction(
        client, amount, from_token.hex, to_token.hex, user.address, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(
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
