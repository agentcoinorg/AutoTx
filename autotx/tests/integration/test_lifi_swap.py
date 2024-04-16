import json
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi import Lifi
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo


def test_swap_through_safe(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)

    eth_address = ETHAddress(network_info.tokens["eth"], client.w3)
    usdc_address = ETHAddress(network_info.tokens["usdc"], client.w3)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], client.w3)
    shib_address = ETHAddress(network_info.tokens["shib"], client.w3)

    balance = manager.balance_of(usdc_address)
    print(balance)

    transactions = build_swap_transaction(
        client,
        1,
        eth_address,
        usdc_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(transactions[0].tx)
    manager.wait(hash)
    balance = manager.balance_of(usdc_address)
    print(balance)

    transactions = build_swap_transaction(
        client,
        2000,
        usdc_address,
        wbtc_address,
        manager.address,
        True,
        network_info.chain_id,
    )

    hash = manager.send_tx(transactions[0].tx)
    manager.wait(hash)
    hash = manager.send_tx(transactions[1].tx)
    manager.wait(hash)
    balance = manager.balance_of(wbtc_address)
    print(balance)


    transactions = build_swap_transaction(
        client,
        0.01,
        wbtc_address,
        shib_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(transactions[0].tx)
    manager.wait(hash)
    hash = manager.send_tx(transactions[1].tx)
    manager.wait(hash)
    balance = manager.balance_of(shib_address)
    print(balance)
