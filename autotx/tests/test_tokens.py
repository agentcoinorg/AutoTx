from autotx.patch import patch_langchain
from autotx.utils.ethereum import get_erc20_balance, load_w3
from autotx.utils.ethereum.constants import SUPPORTED_NETWORKS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_eth_balance import get_eth_balance

patch_langchain()

def test_auto_tx_send_eth(configuration, auto_tx):
    (_, _, client, _) = configuration
    reciever = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)
    balance = get_eth_balance(client.w3, reciever)
    assert balance == 0

    auto_tx.run("Send 1 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, reciever)
    assert balance == 1 * 10**18

def test_auto_tx_send_eth_twice(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration
    reciever = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)

    balance = get_erc20_balance(client.w3, mock_erc20, reciever)
    assert balance == 0

    auto_tx.run("Send 1 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, reciever)
    assert balance == 1 * 10**18

    auto_tx.run("Send 0.5 ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", non_interactive=True)

    balance = get_eth_balance(client.w3, reciever)
    assert balance == 1.5 * 10**18

def test_auto_tx_swap(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
    usdc_address = network_info.tokens["usdc"]

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

        assert balance + 100 * 10**6 == new_balance


def test_auto_tx_send_erc20(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration

    reciever = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)

    prompts = [
        f"Send 10 TT to {reciever}",
        f"Transfer 10 TT to the address {reciever}",
        f"Dispatch 10 TT to wallet {reciever}",
        f"Send 10 TT coins to the Ethereum address {reciever}",
        f"Execute a transaction of 10 TT to address {reciever}",
        f"Move 10 TT to the following address: {reciever}",
        f"Process a payment of 10 TT to the destination {reciever}",
        f"Forward 10 TT to the specific address {reciever}",
        f"Allocate 10 TT to be sent to {reciever}",
        f"Complete sending 10 TT to the address {reciever}",
        f"Initiate the transfer of 10 TT to address {reciever}",
    ]

    for prompt in prompts:
        balance = get_erc20_balance(client.w3, mock_erc20, reciever)

        auto_tx.run(prompt, non_interactive=True)

        new_balance = get_erc20_balance(client.w3, mock_erc20, reciever)

        assert balance + 10 * 10**18 == new_balance


def test_auto_tx_multiple_sends(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration

    reciever_one = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)
    reciever_two = ETHAddress("0x20f8Bf6a479F320EaD074411a4b0e7944eA8c9C1", client.w3)

    prompts = [
        f"Send 10 TT to {reciever_one} and 20 TT to {reciever_two}",
        f"Transfer 10 TT to {reciever_one} and 20 TT to {reciever_two}",
        f"Send 10 TT to address {reciever_one} and 20 TT to address {reciever_two}",
        f"Dispatch 10 TT to the wallet {reciever_one} and 20 TT to the wallet {reciever_two}",
        f"Execute two transactions: send 10 TT to {reciever_one} and 20 TT to {reciever_two}",
        f"Process a payment of 10 TT to {reciever_one} and another payment of 20 TT to {reciever_two}",
        f"Forward 10 TT to address {reciever_one} and 20 TT to address {reciever_two}",
        f"Allocate 10 TT for {reciever_one} and 20 TT for {reciever_two}",
        f"Initiate the transfer of 10 TT to {reciever_one} and 20 TT to {reciever_two}",
        f"Complete the transaction of sending 10 TT to the Ethereum address {reciever_one} and 20 TT to the Ethereum address {reciever_two}",
        f"Move 10 TT to {reciever_one} and 20 TT to {reciever_two} in two separate transactions",
    ]

    for prompt in prompts:
        balance_one = get_erc20_balance(client.w3, mock_erc20, reciever_one)
        balance_two = get_erc20_balance(client.w3, mock_erc20, reciever_two)

        auto_tx.run(prompt, non_interactive=True)

        new_balance_one = get_erc20_balance(client.w3, mock_erc20, reciever_one)
        new_balance_two = get_erc20_balance(client.w3, mock_erc20, reciever_two)
        assert balance_one + 10 * 10**18 == new_balance_one
        assert balance_two + 20 * 10**18 == new_balance_two


def test_auto_tx_swap_and_send(configuration, auto_tx):
    (_, _, client, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
    usdc_address = network_info.tokens["usdc"]
    wbtc_address = network_info.tokens["wbtc"]

    reciever = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)

    prompts = [
        f"Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC and send 50 USDC to {reciever}",
        f"Convert ETH to 0.05 WBTC, subsequently exchange 0.05 WBTC for 1000 USDC, and finally transfer 50 USDC to {reciever}",
        f"Swap Ethereum for 0.05 Wrapped Bitcoin (WBTC), then trade 0.05 WBTC for 1000 USDC, and send 50 USDC to the address {reciever}",
        f"First, exchange ETH for 0.05 WBTC. Following that, convert the 0.05 WBTC into 1000 USDC. Lastly, dispatch 50 USDC to the wallet {reciever}",
        f"Initiate a swap from ETH to 0.05 WBTC, proceed to exchange the WBTC for 1000 USDC, and conclude by transferring 50 USDC to {reciever}",
        f"Begin with converting ETH into 0.05 WBTC, then swap this WBTC for 1000 USDC, and end by sending 50 USDC to the Ethereum address {reciever}",
        f"Execute a series of transactions starting with ETH to 0.05 WBTC conversion, followed by turning 0.05 WBTC into 1000 USDC, and finally, forwarding 50 USDC to {reciever}",
        f"Perform a swap from ETH to 0.05 WBTC, next swap that WBTC to 1000 USDC, and then make a transfer of 50 USDC to the address {reciever}",
        f"Exchange Ethereum for 0.05 WBTC, subsequently convert that WBTC to 1000 USDC, and proceed to send 50 USDC to the designated address {reciever}",
        f"Start by swapping ETH for 0.05 WBTC, follow up by converting this WBTC to 1000 USDC, and conclude the process by transferring 50 USDC to {reciever}",
        f"Initiate with the conversion of ETH to 0.05 WBTC, follow through by swapping the 0.05 WBTC for 1000 USDC, and finalize by sending 50 USDC to {reciever}",
    ]

    for prompt in prompts:
        wbtc_safe_address = manager.balance_of(wbtc_address)
        usdc_safe_address = manager.balance_of(usdc_address)
        reciever_usdc_balance = get_erc20_balance(client.w3, usdc_address, reciever)

        auto_tx.run(prompt, non_interactive=True)

        new_wbtc_safe_address = manager.balance_of(wbtc_address)
        new_usdc_safe_address = manager.balance_of(usdc_address)
        new_reciever_usdc_balance = get_erc20_balance(client.w3, usdc_address, reciever)
        assert new_wbtc_safe_address > wbtc_safe_address
        assert new_usdc_safe_address == usdc_safe_address + 950 * 10**6
        assert new_reciever_usdc_balance == reciever_usdc_balance + 50 * 10**6
