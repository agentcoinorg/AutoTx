from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.helpers.show_address_balances import (
    usdc_address,
    wbtc_address,
)

patch_langchain()


def test_auto_tx_swap(configuration, auto_tx):
    (_, _, _, manager) = configuration
    balance = manager.balance_of(usdc_address)
    assert balance == 0

    auto_tx.run("Buy 100 USDC with ETH")

    balance = manager.balance_of(usdc_address)
    assert balance == 100 * 10**6


def test_auto_tx_send(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration
    reciever = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

    balance = get_erc20_balance(client.w3, mock_erc20, reciever)
    assert balance == 0

    auto_tx.run("Send 10 TT to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1")

    get_erc20_balance(client.w3, mock_erc20, reciever)
    balance = get_erc20_balance(client.w3, mock_erc20, reciever)
    assert balance == 10 * 10**18


def test_auto_tx_multiple_sends(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration
    reciever_one = "0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1"
    reciever_two = "0x20f8Bf6a479F320EaD074411a4b0e7944eA8c9C1"

    balance_one = get_erc20_balance(client.w3, mock_erc20, reciever_one)
    assert balance_one == 0
    balance_two = get_erc20_balance(client.w3, mock_erc20, reciever_two)
    assert balance_two == 0

    auto_tx.run(f"Send 10 TT to {reciever_one} and 20 TT to {reciever_two}")

    balance_one = get_erc20_balance(client.w3, mock_erc20, reciever_one)
    assert balance_one == 10 * 10**18
    balance_two = get_erc20_balance(client.w3, mock_erc20, reciever_two)
    assert balance_two == 20 * 10**18


def test_auto_tx_swap_and_send(configuration, auto_tx):
    (_, _, client, manager) = configuration
    reciever = "0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1"

    wbtc_safe_address = manager.balance_of(wbtc_address)
    assert wbtc_safe_address == 0
    usdc_safe_address = manager.balance_of(usdc_address)
    assert usdc_safe_address == 0
    reciever_usdc_balance = get_erc20_balance(client.w3, usdc_address, reciever)
    assert reciever_usdc_balance == 0

    auto_tx.run(
        f"Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {reciever}"
    )

    wbtc_safe_address = manager.balance_of(wbtc_address)
    assert wbtc_safe_address > 0
    usdc_safe_address = manager.balance_of(usdc_address)
    assert usdc_safe_address == 950 * 10**6
    reciever_usdc_balance = get_erc20_balance(client.w3, usdc_address, reciever)
    assert reciever_usdc_balance == 50 * 10**6
