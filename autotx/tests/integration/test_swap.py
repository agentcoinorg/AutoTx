from decimal import Decimal
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo

DIFFERENCE_PERCENTAGE = 1.01


def test_buy_one_usdc(configuration):
    (_, _, client, manager, _) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    expected_usdc_amount = 1
    buy_usdc_with_eth_transaction = build_swap_transaction(
        client.w3,
        expected_usdc_amount,
        eth_address,
        usdc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_usdc_with_eth_transaction[0].params)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert expected_usdc_amount <= usdc_balance  <= expected_usdc_amount * DIFFERENCE_PERCENTAGE


def test_buy_one_thousand_usdc(configuration):
    (_, _, client, manager, _) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    expected_usdc_amount = 1000
    buy_usdc_with_eth_transaction = build_swap_transaction(
        client.w3,
        expected_usdc_amount,
        eth_address,
        usdc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    print(buy_usdc_with_eth_transaction[0].summary)
    hash = manager.send_tx(buy_usdc_with_eth_transaction[0].params)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert expected_usdc_amount <= usdc_balance <= expected_usdc_amount * DIFFERENCE_PERCENTAGE


def test_receive_native(configuration):
    (_, _, client, manager, _) = configuration

    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    safe_eth_balance = manager.balance_of()
    assert safe_eth_balance == 10
    buy_usdc_with_eth_transaction = build_swap_transaction(
        client.w3,
        5,
        eth_address,
        usdc_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_usdc_with_eth_transaction[0].params)
    manager.wait(hash)
    safe_eth_balance = manager.balance_of()
    assert safe_eth_balance == 5

    buy_eth_with_usdc_transaction = build_swap_transaction(
        client.w3,
        4,
        usdc_address,
        eth_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_eth_with_usdc_transaction[0].params)
    manager.wait(hash)
    hash = manager.send_tx(buy_eth_with_usdc_transaction[1].params)
    manager.wait(hash)
    safe_eth_balance = manager.balance_of()
    assert safe_eth_balance >= 9


def test_buy_small_amount_wbtc_with_eth(configuration):
    (_, _, client, manager, _) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    expected_wbtc_amount = 0.01
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        client.w3,
        Decimal(str(expected_wbtc_amount)),
        eth_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_wbtc_with_eth_transaction[0].params)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE


def test_buy_big_amount_wbtc_with_eth(configuration):
    (_, _, client, manager, _) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    expected_wbtc_amount = 0.1
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        client.w3,
        Decimal(str(expected_wbtc_amount)),
        eth_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )
    hash = manager.send_tx(buy_wbtc_with_eth_transaction[0].params)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE


def test_swap_multiple_tokens(configuration):
    (_, _, client, manager, _) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)

    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    shib_address = ETHAddress(network_info.tokens["shib"])

    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance == 0

    sell_eth_for_usdc_transaction = build_swap_transaction(
        client.w3,
        1,
        eth_address,
        usdc_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(sell_eth_for_usdc_transaction[0].params)
    manager.wait(hash)
    usdc_balance = manager.balance_of(usdc_address)
    assert usdc_balance > 2900

    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance == 0

    buy_wbtc_with_usdc_transaction = build_swap_transaction(
        client.w3,
        0.01,
        usdc_address,
        wbtc_address,
        manager.address,
        False,
        network_info.chain_id,
    )

    hash = manager.send_tx(buy_wbtc_with_usdc_transaction[0].params)
    manager.wait(hash)
    hash = manager.send_tx(buy_wbtc_with_usdc_transaction[1].params)
    manager.wait(hash)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert wbtc_balance >= 0.01

    shib_balance = manager.balance_of(shib_address)
    assert shib_balance == 0

    sell_wbtc_for_shib = build_swap_transaction(
        client.w3,
        0.005,
        wbtc_address,
        shib_address,
        manager.address,
        True,
        network_info.chain_id,
    )
    hash = manager.send_tx(sell_wbtc_for_shib[0].params)
    manager.wait(hash)
    hash = manager.send_tx(sell_wbtc_for_shib[1].params)
    manager.wait(hash)
    shib_balance = manager.balance_of(shib_address)
    shib_balance = manager.balance_of(shib_address)
    assert shib_balance > 0
