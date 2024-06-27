import asyncio
from decimal import Decimal
from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance
from autotx.utils.ethereum.get_native_balance import get_native_balance
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo

DIFFERENCE_PERCENTAGE = 1.01


def test_buy_one_usdc(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    expected_usdc_amount = 1
    buy_usdc_with_eth_transaction = build_swap_transaction(
        smart_account.web3,
        expected_usdc_amount,
        eth_address,
        usdc_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )
    hash = smart_account.send_tx(buy_usdc_with_eth_transaction[0].params)
    smart_account.wait(hash)
    usdc_balance = get_erc20_balance(smart_account.web3, usdc_address, smart_account.address)
    assert expected_usdc_amount <= usdc_balance  <= expected_usdc_amount * DIFFERENCE_PERCENTAGE


def test_buy_one_thousand_usdc(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    expected_usdc_amount = 1000
    buy_usdc_with_eth_transaction = build_swap_transaction(
        smart_account.web3,
        expected_usdc_amount,
        eth_address,
        usdc_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )
    print(buy_usdc_with_eth_transaction[0].summary)
    hash = asyncio.run(smart_account.send_transaction(buy_usdc_with_eth_transaction[0].params))
    smart_account.wait(hash)
    usdc_balance = get_erc20_balance(smart_account.web3, usdc_address, smart_account.address)
    assert expected_usdc_amount <= usdc_balance <= expected_usdc_amount * DIFFERENCE_PERCENTAGE


def test_receive_native(smart_account):

    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    safe_eth_balance = get_native_balance(smart_account.web3, smart_account.address)
    assert safe_eth_balance == 10
    buy_usdc_with_eth_transaction = build_swap_transaction(
        smart_account.web3,
        5,
        eth_address,
        usdc_address,
        smart_account.address,
        True,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(buy_usdc_with_eth_transaction[0].params))
    smart_account.wait(hash)
    safe_eth_balance = get_native_balance(smart_account.web3, smart_account.address)
    assert safe_eth_balance == 5

    buy_eth_with_usdc_transaction = build_swap_transaction(
        smart_account.web3,
        4,
        usdc_address,
        eth_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(buy_eth_with_usdc_transaction[0].params))
    smart_account.wait(hash)
    hash = asyncio.run(smart_account.send_transaction(buy_eth_with_usdc_transaction[1].params))
    smart_account.wait(hash)
    safe_eth_balance = get_native_balance(smart_account.web3, smart_account.address)
    assert safe_eth_balance >= 9


def test_buy_small_amount_wbtc_with_eth(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    expected_wbtc_amount = 0.01
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        smart_account.web3,
        Decimal(str(expected_wbtc_amount)),
        eth_address,
        wbtc_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(buy_wbtc_with_eth_transaction[0].params))
    smart_account.wait(hash)
    wbtc_balance = get_erc20_balance(smart_account.web3, wbtc_address, smart_account.address)
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE


def test_buy_big_amount_wbtc_with_eth(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    eth_address = ETHAddress(network_info.tokens["eth"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    expected_wbtc_amount = 0.1
    buy_wbtc_with_eth_transaction = build_swap_transaction(
        smart_account.web3,
        Decimal(str(expected_wbtc_amount)),
        eth_address,
        wbtc_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(buy_wbtc_with_eth_transaction[0].params))
    smart_account.wait(hash)
    wbtc_balance = get_erc20_balance(smart_account.web3, wbtc_balance, smart_account.address)
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE


def test_swap_multiple_tokens(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)

    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])
    shib_address = ETHAddress(network_info.tokens["shib"])

    usdc_balance = get_erc20_balance(smart_account.web3, usdc_address, smart_account.address)
    assert usdc_balance == 0

    sell_eth_for_usdc_transaction = build_swap_transaction(
        smart_account.web3,
        1,
        eth_address,
        usdc_address,
        smart_account.address,
        True,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(sell_eth_for_usdc_transaction[0].params))
    smart_account.wait(hash)
    usdc_balance = get_erc20_balance(smart_account.web3, usdc_address, smart_account.address)
    assert usdc_balance > 2900

    wbtc_balance = get_erc20_balance(smart_account.web3, wbtc_address, smart_account.address)
    assert wbtc_balance == 0

    buy_wbtc_with_usdc_transaction = build_swap_transaction(
        smart_account.web3,
        0.01,
        usdc_address,
        wbtc_address,
        smart_account.address,
        False,
        network_info.chain_id,
    )

    hash = asyncio.run(smart_account.send_transaction(buy_wbtc_with_usdc_transaction[0].params))
    smart_account.wait(hash)
    hash = asyncio.run(smart_account.send_transaction(buy_wbtc_with_usdc_transaction[1].params))
    smart_account.wait(hash)
    wbtc_balance = get_erc20_balance(smart_account.web3, wbtc_address, smart_account.address)
    assert wbtc_balance >= 0.01

    shib_balance = get_erc20_balance(smart_account.web3, shib_address, smart_account.address)
    assert shib_balance == 0

    sell_wbtc_for_shib = build_swap_transaction(
        smart_account.web3,
        0.005,
        wbtc_address,
        shib_address,
        smart_account.address,
        True,
        network_info.chain_id,
    )
    hash = asyncio.run(smart_account.send_transaction(sell_wbtc_for_shib[0].params))
    smart_account.wait(hash)
    hash = asyncio.run(smart_account.send_transaction(sell_wbtc_for_shib[1].params))
    smart_account.wait(hash)
    shib_balance = get_erc20_balance(smart_account.web3, shib_address, smart_account.address)
    shib_balance = get_erc20_balance(smart_account.web3, shib_address, smart_account.address)
    assert shib_balance > 0
