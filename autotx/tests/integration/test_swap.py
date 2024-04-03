from autotx.utils.ethereum import (
    get_erc20_balance,
    get_eth_balance,
)
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction

def test_swap(configuration):
    (user, _, client, _) = configuration

    network_info = NetworkInfo(client.w3.eth.chain_id)
    weth_address = ETHAddress(network_info.tokens["weth"], client.w3)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], client.w3)

    user_addr = ETHAddress(user.address, client.w3)

    balance = get_erc20_balance(client.w3, wbtc_address, user_addr)
    assert balance == 0

    txs = build_swap_transaction(
        client, 0.05, weth_address.hex, wbtc_address.hex, user_addr.hex, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(
            {
                **tx.tx,
                "nonce": client.w3.eth.get_transaction_count(user_addr.hex),
                "gas": 200000,
            }
        )

        hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = client.w3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction #{i} failed ")
            break

    new_balance = get_erc20_balance(client.w3, wbtc_address, user_addr)
    assert new_balance == 0.05

def test_swap_recieve_eth(configuration):
    (user, _, client, _) = configuration

    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"], client.w3)
    usdc_address = ETHAddress(network_info.tokens["usdc"], client.w3)

    user_addr = ETHAddress(user.address, client.w3)

    balance = get_eth_balance(client.w3, user_addr)
    assert int(balance) == 9989

    tx = build_swap_transaction(
        client, 5, eth_address.hex, usdc_address.hex, user_addr.hex, True
    )

    transaction = user.sign_transaction(
        {
            **tx[0].tx,
            "nonce": client.w3.eth.get_transaction_count(user_addr.hex),
            "gas": 200000,
        }
    )

    hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

    receipt = client.w3.eth.wait_for_transaction_receipt(hash)

    if receipt["status"] == 0:
        print(f"Transaction to swap ETH -> USDC failed ")

    balance = get_eth_balance(client.w3, user_addr)
    assert int(balance) == 9984

    txs = build_swap_transaction(
        client, 4, usdc_address.hex, eth_address.hex, user_addr.hex, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(
            {
                **tx.tx,
                "nonce": client.w3.eth.get_transaction_count(user_addr.hex),
                "gas": 200000,
            }
        )

        hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = client.w3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction #{i} to swap USDC -> ETH failed ")
            break

    balance = get_eth_balance(client.w3, user_addr)
    assert int(balance) == 9988

def test_swap_through_safe(configuration):
    (_, _, client, manager) = configuration

    network_info = NetworkInfo(client.w3.eth.chain_id)
    weth_address = ETHAddress(network_info.tokens["weth"], client.w3)
    usdc_address = ETHAddress(network_info.tokens["usdc"], client.w3)

    balance = manager.balance_of(usdc_address)
    assert balance == 0

    txs = build_swap_transaction(
        client, 6000, weth_address.hex, usdc_address.hex, manager.address.hex, False
    )

    hash = manager.send_tx_batch(txs, require_approval=False)
    manager.wait(hash)

    new_balance = manager.balance_of(usdc_address)
    assert new_balance == 6000
