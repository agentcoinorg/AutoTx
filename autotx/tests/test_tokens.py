from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance, load_w3
from autotx.utils.ethereum.constants import SUPPORTED_NETWORKS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_eth_balance import get_eth_balance

patch_langchain()

def test_auto_tx_send_eth(configuration, auto_tx):
    (_, _, client, _) = configuration
    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    auto_tx.run("Send 1 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

def test_auto_tx_send_eth_twice(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration
    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)

    balance = get_erc20_balance(client.w3, mock_erc20, receiver)
    assert balance == 0

    auto_tx.run("Send 1 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

    auto_tx.run("Send 0.5 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1.5

def test_auto_tx_send_erc20(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration

    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)

    prompt = f"Send 10 TTOK to {receiver}"

    balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    assert balance + 10 == new_balance
      
def test_auto_tx_multiple_sends(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration

    receiver_one = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)
    receiver_two = ETHAddress("0x20f8Bf6a479F320EaD074411a4b0e7944eA8c9C1", client.w3)

    prompt = f"Send 10 TTOK to {receiver_one} and 20 TTOK to {receiver_two}"
        
    balance_one = get_erc20_balance(client.w3, mock_erc20, receiver_one)
    balance_two = get_erc20_balance(client.w3, mock_erc20, receiver_two)

    auto_tx.run(prompt, non_interactive=True)

    new_balance_one = get_erc20_balance(client.w3, mock_erc20, receiver_one)
    new_balance_two = get_erc20_balance(client.w3, mock_erc20, receiver_two)

    assert balance_one + 10 == new_balance_one
    assert balance_two + 20 == new_balance_two

def test_auto_tx_swap(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)

    prompt = "Buy 100 USDC with ETH"
    balance = manager.balance_of(usdc_address)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(usdc_address)

    assert balance + 100 == new_balance

def test_auto_tx_swap_and_send(configuration, auto_tx):
    (_, _, client, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
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