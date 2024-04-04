import pytest
from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance, load_w3
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

patch_langchain()

@pytest.mark.skip()
def test_auto_tx_send_erc20(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _) = configuration

    receiver = test_accounts[0]

    prompts = [
        f"Send 10 USDC to {receiver}",
        f"Transfer 10 USDC to the address {receiver}",
        f"Dispatch 10 USDC to wallet {receiver}",
        f"Send 10 USDC coins to the Ethereum address {receiver}",
        f"Execute a transaction of 10 USDC to address {receiver}",
        f"Move 10 USDC to the following address: {receiver}",
        f"Process a payment of 10 USDC to the destination {receiver}",
        f"Forward 10 USDC to the specific address {receiver}",
        f"Allocate 10 USDC to be sent to {receiver}",
        f"Complete sending 10 USDC to the address {receiver}",
        f"Initiate the transfer of 10 USDC to address {receiver}",
    ]

    for prompt in prompts:
        balance = get_erc20_balance(client.w3, usdc, receiver)

        auto_tx.run(prompt, non_interactive=True)

        new_balance = get_erc20_balance(client.w3, usdc, receiver)

        try: 
            assert balance + 10 == new_balance
        except AssertionError:
            print(f"Failed for prompt: {prompt}")
            print(f"Balance: {balance} New Balance: {new_balance}")
            raise

@pytest.mark.skip()
def test_auto_tx_swap(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)

    prompts = [
        "Buy 100 USDC with ETH",
        "Purchase 100 USDC using Ethereum",
        "Convert Ethereum to 100 USDC",
        "Swap ETH for 100 units of USDC",
        "Execute a trade to buy 100 USDC with Ethereum",
        "Use ETH to acquire 100 USDC",
        "Make a transaction to get 100 USDC using ETH",
        "Exchange Ethereum for 100 USDC",
        "Initiate a conversion from ETH to 100 USDC",
        "Complete a deal to purchase 100 USDC using ETH",
        "Carry out a swap of ETH for 100 USDC",
    ]

    for prompt in prompts:
        balance = manager.balance_of(usdc_address)

        auto_tx.run(prompt, non_interactive=True)

        new_balance = manager.balance_of(usdc_address)

        try:
            assert balance + 100 == new_balance
        except AssertionError:
            print(f"Failed for prompt: {prompt}")
            print(f"Balance: {balance} New Balance: {new_balance}")
            raise

@pytest.mark.skip()
def test_auto_tx_multiple_sends(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _) = configuration

    receiver_one = test_accounts[0]
    receiver_two = test_accounts[1]

    prompts = [
        f"Send 10 USDC to {receiver_one} and 20 USDC to {receiver_two}",
        f"Transfer 10 USDC to {receiver_one} and 20 USDC to {receiver_two}",
        f"Send 10 USDC to address {receiver_one} and 20 USDC to address {receiver_two}",
        f"Dispatch 10 USDC to the wallet {receiver_one} and 20 USDC to the wallet {receiver_two}",
        f"Execute two transactions: send 10 USDC to {receiver_one} and 20 USDC to {receiver_two}",
        f"Process a payment of 10 USDC to {receiver_one} and another payment of 20 USDC to {receiver_two}",
        f"Forward 10 USDC to address {receiver_one} and 20 USDC to address {receiver_two}",
        f"Allocate 10 USDC for {receiver_one} and 20 USDC for {receiver_two}",
        f"Initiate the transfer of 10 USDC to {receiver_one} and 20 USDC to {receiver_two}",
        f"Complete the transaction of sending 10 USDC to the Ethereum address {receiver_one} and 20 USDC to the Ethereum address {receiver_two}",
        f"Move 10 USDC to {receiver_one} and 20 USDC to {receiver_two} in two separate transactions",
    ]

    for prompt in prompts:
        balance_one = get_erc20_balance(client.w3, usdc, receiver_one)
        balance_two = get_erc20_balance(client.w3, usdc, receiver_two)

        auto_tx.run(prompt, non_interactive=True)

        new_balance_one = get_erc20_balance(client.w3, usdc, receiver_one)
        new_balance_two = get_erc20_balance(client.w3, usdc, receiver_two)

        try:
            assert balance_one + 10 == new_balance_one
            assert balance_two + 20 == new_balance_two
        except AssertionError:
            print(f"Failed for prompt: {prompt}")
            print(f"Balance One: {balance_one} New Balance One: {new_balance_one}")
            print(f"Balance Two: {balance_two} New Balance Two: {new_balance_two}")
            raise

@pytest.mark.skip()
def test_auto_tx_swap_and_send(configuration, auto_tx, test_accounts):
    (_, _, client, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], web3)

    receiver = test_accounts[0]

    prompts = [
        f"Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {receiver}",
        f"Convert ETH to 0.05 WBTC, subsequently exchange 0.05 WBTC for 1000 USDC, and finally transfer 50 USDC to {receiver}",
        f"Swap Ethereum for 0.05 Wrapped Bitcoin (WBTC), then trade 0.05 WBTC for 1000 USDC, and send 50 USDC to the address {receiver}",
        f"First, exchange ETH for 0.05 WBTC. Following that, convert the 0.05 WBTC into 1000 USDC. Lastly, dispatch 50 USDC to the wallet {receiver}",
        f"Initiate a swap from ETH to 0.05 WBTC, proceed to exchange the WBTC for 1000 USDC, and conclude by transferring 50 USDC to {receiver}",
        f"Begin with converting ETH into 0.05 WBTC, then swap this WBTC for 1000 USDC, and end by sending 50 USDC to the Ethereum address {receiver}",
        f"Execute a series of transactions starting with ETH to 0.05 WBTC conversion, followed by turning 0.05 WBTC into 1000 USDC, and finally, forwarding 50 USDC to {receiver}",
        f"Perform a swap from ETH to 0.05 WBTC, next swap that WBTC to 1000 USDC, and then make a transfer of 50 USDC to the address {receiver}",
        f"Exchange Ethereum for 0.05 WBTC, subsequently convert that WBTC to 1000 USDC, and proceed to send 50 USDC to the designated address {receiver}",
        f"Start by swapping ETH for 0.05 WBTC, follow up by converting this WBTC to 1000 USDC, and conclude the process by transferring 50 USDC to {receiver}",
        f"Initiate with the conversion of ETH to 0.05 WBTC, follow through by swapping the 0.05 WBTC for 1000 USDC, and finalize by sending 50 USDC to {receiver}",
    ]

    for prompt in prompts:
        wbtc_safe_address = manager.balance_of(wbtc_address)
        usdc_safe_address = manager.balance_of(usdc_address)
        receiver_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver)

        auto_tx.run(prompt, non_interactive=True)

        new_wbtc_safe_address = manager.balance_of(wbtc_address)
        new_usdc_safe_address = manager.balance_of(usdc_address)
        new_receiver_usdc_balance = get_erc20_balance(client.w3, usdc_address, receiver)

        try:
            assert new_wbtc_safe_address > wbtc_safe_address
            assert new_usdc_safe_address == usdc_safe_address + 950
            assert new_receiver_usdc_balance == receiver_usdc_balance + 50
        except AssertionError:
            print(f"Failed for prompt: {prompt}")
            print(f"WBTC Balance: {wbtc_safe_address} New WBTC Balance: {new_wbtc_safe_address}")
            print(f"USDC Balance: {usdc_safe_address} New USDC Balance: {new_usdc_safe_address}")
            print(f"receiver USDC Balance: {receiver_usdc_balance} New receiver USDC Balance: {new_receiver_usdc_balance}")
            raise
