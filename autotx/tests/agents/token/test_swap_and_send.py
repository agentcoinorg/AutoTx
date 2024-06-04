from autotx.utils.ethereum import get_erc20_balance, get_native_balance
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

DIFFERENCE_PERCENTAGE = 1.01

def test_swap_and_send_simple(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    receiver = test_accounts[0]

    prompt = f"Swap ETH to 0.05 WBTC, and send 0.01 WBTC to {receiver}"

    auto_tx.run(prompt, non_interactive=True)

    new_wbtc_safe_address = manager.balance_of(wbtc_address)
    new_receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)
    excepted_safe_wbtc_balance = 0.04
    assert excepted_safe_wbtc_balance <= new_wbtc_safe_address <= new_wbtc_safe_address * DIFFERENCE_PERCENTAGE
    assert new_receiver_wbtc_balance == 0.01

def test_swap_and_send_complex(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    receiver = test_accounts[0]

    prompt = f"Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {receiver}"

    wbtc_safe_address = manager.balance_of(wbtc_address)
    auto_tx.run(prompt, non_interactive=True)

    new_wbtc_safe_address = manager.balance_of(wbtc_address)
    new_usdc_safe_address = manager.balance_of(usdc_address)
    new_receiver_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver)

    expected_usdc_safe_balance = 950
    assert new_wbtc_safe_address > wbtc_safe_address
    assert expected_usdc_safe_balance <= new_usdc_safe_address <= expected_usdc_safe_balance * DIFFERENCE_PERCENTAGE
    assert new_receiver_usdc_balance == 50

def test_send_and_swap_simple(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    receiver = test_accounts[0]

    prompt = f"Send 0.1 ETH to {receiver}, and then swap ETH to 0.05 WBTC"

    receiver_native_balance = get_native_balance(client.w3, receiver)
    receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    auto_tx.run(prompt, non_interactive=True)

    safe_wbtc_balance = manager.balance_of(wbtc_address)
    new_receiver_native_balance = get_native_balance(client.w3, receiver)
    new_receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    expected_wbtc_safe_balance = 0.05
    assert expected_wbtc_safe_balance <= safe_wbtc_balance <= expected_wbtc_safe_balance * DIFFERENCE_PERCENTAGE
    assert receiver_wbtc_balance == 0
    assert new_receiver_wbtc_balance == receiver_wbtc_balance
    assert new_receiver_native_balance == receiver_native_balance + 0.1

def test_send_and_swap_complex(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]

    prompt = f"Send 0.1 ETH to {receiver_1}, then swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {receiver_2}"

    wbtc_safe_balance = manager.balance_of(wbtc_address)
    receiver_1_native_balance = get_native_balance(client.w3, receiver_1)
    receiver_2_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver_2)

    auto_tx.run(prompt, non_interactive=True)

    new_wbtc_safe_balance = manager.balance_of(wbtc_address)
    new_usdc_safe_balance = manager.balance_of(usdc_address)
    new_receiver_1_native_balance = get_native_balance(client.w3, receiver_1)
    new_receiver_1_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver_1)
    new_receiver_1_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver_1)
    new_receiver_2_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver_2)
    new_receiver_2_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver_2)
    expected_usdc_safe_balance = 950
    assert expected_usdc_safe_balance <= new_usdc_safe_balance <= expected_usdc_safe_balance * DIFFERENCE_PERCENTAGE
    assert new_wbtc_safe_balance > wbtc_safe_balance
    assert new_receiver_1_native_balance == receiver_1_native_balance + 0.1
    assert new_receiver_1_usdc_balance == 0
    assert new_receiver_1_wbtc_balance == 0
    assert new_receiver_2_usdc_balance == receiver_2_usdc_balance + 50
    assert new_receiver_2_wbtc_balance == 0