from decimal import Decimal
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo

PLUS_DIFFERENCE_PERCENTAGE = 0.007


def test_buy_one_usdc(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    desired_amount = 1
    buy_usdc_with_eth_transaction = build_swap_transaction(
        client,
        desired_amount,
        eth_address,
        usdc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_usdc_with_eth_transaction[0].tx)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance >= desired_amount and usdc_balance <= desired_amount + (
        desired_amount * PLUS_DIFFERENCE_PERCENTAGE
    )

def test_buy_one_thousand_usdc(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    desired_amount = 1000
    buy_usdc_with_eth_transaction = build_swap_transaction(
        client,
        desired_amount,
        eth_address,
        usdc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    print(buy_usdc_with_eth_transaction[0].summary)
    hash = manager.send_tx(buy_usdc_with_eth_transaction[0].tx)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance >= desired_amount and usdc_balance <= desired_amount + (
        desired_amount * PLUS_DIFFERENCE_PERCENTAGE
    )

def test_buy_small_amount_wbtc_with_eth(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    desired_amount = 0.01
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        client,
        Decimal(desired_amount),
        eth_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_wbtc_with_eth_transaction[0].tx)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance >= desired_amount and wbtc_balance <= desired_amount + (
        desired_amount * PLUS_DIFFERENCE_PERCENTAGE
    )

def test_buy_big_amount_wbtc_with_eth(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    desired_amount = 0.1
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        client,
        Decimal(desired_amount),
        eth_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_wbtc_with_eth_transaction[0].tx)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance >= desired_amount and wbtc_balance <= desired_amount + (
        desired_amount * PLUS_DIFFERENCE_PERCENTAGE
    )


def test_swap_multiple_tokens(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)

    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    shib_address = ETHAddress(network_info.tokens["shib"])

    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance == 0

    sell_eth_for_usdc_transaction = build_swap_transaction(
        client,
        1,
        eth_address,
        usdc_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(sell_eth_for_usdc_transaction[0].tx)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance > 2900

    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance == 0

    buy_wbtc_with_usdc_transaction = build_swap_transaction(
        client,
        0.01,
        usdc_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )

    hash = manager.send_tx(buy_wbtc_with_usdc_transaction[0].tx)
    manager.wait(hash)
    hash = manager.send_tx(buy_wbtc_with_usdc_transaction[1].tx)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance >= 0.01

    shib_balance = manager.balance_of(shib_address)
    assert shib_balance == 0

    sell_wbtc_for_shib = build_swap_transaction(
        client,
        0.005,
        wbtc_address,
        shib_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(sell_wbtc_for_shib[0].tx)
    manager.wait(hash)
    hash = manager.send_tx(sell_wbtc_for_shib[1].tx)
    manager.wait(hash)
    shib_balance = manager.balance_of(shib_address)
    shib_balance = manager.balance_of(shib_address)
    assert shib_balance > 0
