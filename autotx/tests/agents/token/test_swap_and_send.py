from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance, load_w3
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

patch_langchain()

def test_auto_tx_swap_and_send_simple(configuration, auto_tx):
    (_, _, client, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], web3)

    receiver = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)

    prompt = f"Swap ETH to 0.05 WBTC, and send 0.01 WBTC to {receiver}"

    wbtc_safe_address = manager.balance_of(wbtc_address)
    receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_wbtc_safe_address = manager.balance_of(wbtc_address)
    new_receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    assert new_wbtc_safe_address == wbtc_safe_address + 0.04
    assert new_receiver_wbtc_balance == receiver_wbtc_balance + 0.01

def test_auto_tx_swap_and_send_complex(configuration, auto_tx):
    (_, _, client, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], web3)

    receiver = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)

    prompt = f"Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {receiver}"

    wbtc_safe_address = manager.balance_of(wbtc_address)
    usdc_safe_address = manager.balance_of(usdc_address)
    receiver_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_wbtc_safe_address = manager.balance_of(wbtc_address)
    new_usdc_safe_address = manager.balance_of(usdc_address)
    new_receiver_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver)

    assert new_wbtc_safe_address > wbtc_safe_address
    assert new_usdc_safe_address == usdc_safe_address + 950
    assert new_receiver_usdc_balance == receiver_usdc_balance + 50