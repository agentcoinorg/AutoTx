from autotx.utils.ethereum import (
    get_erc20_balance,
)
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction
from autotx.utils.ethereum.helpers.show_address_balances import (
    weth_address,
    usdc_address,
    wbtc_address,
)


def test_swap(configuration):
    (user, _, client, _) = configuration

    balance = get_erc20_balance(client.w3, wbtc_address, user.address)
    assert balance == 0

    txs = build_swap_transaction(
        client, 0.05, weth_address, wbtc_address, user.address, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(
            {
                **tx,
                "nonce": client.w3.eth.get_transaction_count(user.address),
                "gas": 200000,
            }
        )

        hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = client.w3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction #{i} failed ")
            break

    new_balance = get_erc20_balance(client.w3, wbtc_address, user.address)
    assert new_balance == 0.05 * 10**8


def test_swap_through_safe(configuration):
    (_, _, client, manager) = configuration

    balance = manager.balance_of(usdc_address)
    assert balance == 0

    txs = build_swap_transaction(
        client, 6000, weth_address, usdc_address, manager.address, False
    )

    hash = manager.send_multisend_tx(txs)
    manager.wait(hash)

    new_balance = manager.balance_of(usdc_address)
    assert new_balance == 6000 * 10**6
