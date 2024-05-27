from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.get_native_balance import get_native_balance

def test_send_native(configuration, auto_tx, test_accounts):
    (_, _, client, _, _) = configuration
    receiver = test_accounts[0]
    balance = get_native_balance(client.w3, receiver)
    assert balance == 0

    auto_tx.run(f"Send 1 ETH to {receiver}", non_interactive=True)

    balance = get_native_balance(client.w3, receiver)
    assert balance == 1

def test_send_erc20(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _, _) = configuration

    receiver = test_accounts[0]

    prompt = f"Send 10 USDC to {receiver}"

    balance = get_erc20_balance(client.w3, usdc, receiver)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, usdc, receiver)

    assert balance + 10 == new_balance

def test_send_native_sequential(configuration, auto_tx, test_accounts):
    (_, _, client, _, _) = configuration
    receiver = test_accounts[0]

    auto_tx.run(f"Send 1 ETH to {receiver}", non_interactive=True)

    balance = get_native_balance(client.w3, receiver)
    assert balance == 1

    auto_tx.run(f"Send 0.5 ETH to {receiver}", non_interactive=True)

    balance = get_native_balance(client.w3, receiver)
    assert balance == 1.5
      
def test_send_erc20_parallel(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _, _) = configuration

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

def test_send_eth_multiple(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _, _) = configuration

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]
    receiver_3 = test_accounts[2]
    receiver_4 = test_accounts[3]
    receiver_5 = test_accounts[4]

    prompt = f"Send 1.3 USDC to {receiver_1}, {receiver_2}, {receiver_3}, {receiver_4} and {receiver_5}"
        
    balance_1 = get_erc20_balance(client.w3, usdc, receiver_1)
    balance_2 = get_erc20_balance(client.w3, usdc, receiver_2)
    balance_3 = get_erc20_balance(client.w3, usdc, receiver_3)
    balance_4 = get_erc20_balance(client.w3, usdc, receiver_4)
    balance_5 = get_erc20_balance(client.w3, usdc, receiver_5)

    auto_tx.run(prompt, non_interactive=True)

    new_balance_1 = get_erc20_balance(client.w3, usdc, receiver_1)
    new_balance_2 = get_erc20_balance(client.w3, usdc, receiver_2)
    new_balance_3 = get_erc20_balance(client.w3, usdc, receiver_3)
    new_balance_4 = get_erc20_balance(client.w3, usdc, receiver_4)
    new_balance_5 = get_erc20_balance(client.w3, usdc, receiver_5)

    assert balance_1 + 1.3 == new_balance_1
    assert balance_2+ 1.3 == new_balance_2
    assert balance_3 + 1.3 == new_balance_3
    assert balance_4 + 1.3 == new_balance_4
    assert balance_5 + 1.3 == new_balance_5