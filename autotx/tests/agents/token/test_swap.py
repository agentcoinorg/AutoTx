from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

DIFFERENCE_PERCENTAGE = 1.01

def test_swap_with_non_default_token(configuration, auto_tx):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    shib_address = ETHAddress(network_info.tokens["shib"])

    prompt = "Buy 100000 SHIB with ETH"
    balance = manager.balance_of(shib_address)
    assert balance == 0
    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(shib_address)

    expected_shib_amount = 100000
    assert expected_shib_amount <= new_balance <= expected_shib_amount * DIFFERENCE_PERCENTAGE

def test_swap_native(configuration, auto_tx):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])

    prompt = "Buy 100 USDC with ETH"
    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(usdc_address)
    expected_usdc_amount = 100
    assert expected_usdc_amount <= new_balance <= expected_usdc_amount * DIFFERENCE_PERCENTAGE

def test_swap_multiple_1(configuration, auto_tx):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Buy 1000 USDC with ETH and then buy WBTC with 500 USDC"
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)

    expected_usdc_amount = 500
    usdc_balance = manager.balance_of(usdc_address)
    # 1000 is the amount bought so we need to get the difference from that amount
    expected_usdc_amount_plus_slippage = 1000 * DIFFERENCE_PERCENTAGE
    assert expected_usdc_amount <= usdc_balance <= expected_usdc_amount_plus_slippage - expected_usdc_amount
    assert wbtc_balance < manager.balance_of(wbtc_address)

def test_swap_multiple_2(configuration, auto_tx):
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Sell ETH for 1000 USDC and then sell 500 USDC for WBTC"
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)

    expected_amount = 500
    usdc_balance = manager.balance_of(usdc_address)
    assert expected_amount <= usdc_balance
    assert wbtc_balance < manager.balance_of(wbtc_address)

def test_swap_triple(configuration, auto_tx): 
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    uni_address = ETHAddress(network_info.tokens["uni"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Buy 1 USDC, 0.5 UNI and 0.05 WBTC with ETH"

    auto_tx.run(prompt, non_interactive=True)

    expected_usdc_amount = 1
    expected_uni_amount = 0.5
    expected_wbtc_amount = 0.05
    usdc_balance = manager.balance_of(usdc_address)
    uni_balance = manager.balance_of(uni_address)
    wbtc_balance = manager.balance_of(wbtc_address)
    assert expected_usdc_amount <= usdc_balance <= expected_usdc_amount * DIFFERENCE_PERCENTAGE
    assert expected_uni_amount <= uni_balance <= expected_uni_amount * DIFFERENCE_PERCENTAGE
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE

def test_swap_complex_1(configuration, auto_tx): # This one is complex because it confuses the LLM with WBTC amount
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC"
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)
    expected_usdc_amount = 1000
    usdc_balance = manager.balance_of(usdc_address)
    assert expected_usdc_amount <= usdc_balance <= expected_usdc_amount * DIFFERENCE_PERCENTAGE
    assert wbtc_balance < manager.balance_of(wbtc_address)

def test_swap_complex_2(configuration, auto_tx): # This one is complex because it confuses the LLM with WBTC amount
    (_, _, client, manager, _) = configuration
    web3 = client.w3
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Buy 1000 USDC with ETH, then sell USDC to buy 0.001 WBTC"
    usdc_balance = manager.balance_of(usdc_address)

    auto_tx.run(prompt, non_interactive=True)

    wbtc_balance = manager.balance_of(wbtc_address)
    expected_wbtc_amount = 0.001
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount * DIFFERENCE_PERCENTAGE
    assert usdc_balance < manager.balance_of(usdc_address)
