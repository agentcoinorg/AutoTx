from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance
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

def test_auto_tx_send_erc20(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration

    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)

    prompt = f"Send 10 TTOK to {receiver}"

    balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    assert balance + 10 == new_balance

def test_auto_tx_send_eth_sequential(configuration, auto_tx, mock_erc20):
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
      
def test_auto_tx_send_erc20_parallel(configuration, auto_tx, mock_erc20):
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