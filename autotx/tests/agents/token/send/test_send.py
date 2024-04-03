from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.get_eth_balance import get_eth_balance

patch_langchain()

def test_auto_tx_send_eth(configuration, auto_tx, test_accounts):
    (_, _, client, _) = configuration
    receiver = test_accounts[0]
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    auto_tx.run(f"Send 1 ETH to {receiver}", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

def test_auto_tx_send_erc20(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _) = configuration

    receiver = test_accounts[0]

    prompt = f"Send 10 USDC to {receiver}"

    balance = get_erc20_balance(client.w3, usdc, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, usdc, receiver)

    assert balance + 10 == new_balance

def test_auto_tx_send_eth_sequential(configuration, auto_tx, test_accounts):
    (_, _, client, _) = configuration
    receiver = test_accounts[0]

    auto_tx.run(f"Send 1 ETH to {receiver}", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

    auto_tx.run(f"Send 0.5 ETH to {receiver}", non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1.5
      
def test_auto_tx_send_erc20_parallel(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _) = configuration

    receiver_one = test_accounts[0]
    receiver_two = test_accounts[1]

    prompt = f"Send 2 USDC to {receiver_one} and 3 USDC to {receiver_two}"
        
    balance_one = get_erc20_balance(client.w3, usdc, receiver_one)
    balance_two = get_erc20_balance(client.w3, usdc, receiver_two)

    auto_tx.run(prompt, non_interactive=True)

    new_balance_one = get_erc20_balance(client.w3, usdc, receiver_one)
    new_balance_two = get_erc20_balance(client.w3, usdc, receiver_two)

    assert balance_one + 2 == new_balance_one
    assert balance_two + 3 == new_balance_two