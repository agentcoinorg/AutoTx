from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.lifi.swap import SLIPPAGE
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

PLUS_DIFFERENCE_PERCENTAGE = 0.007

def test_auto_tx_swap_with_non_default_token(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    shib_address = ETHAddress(network_info.tokens["shib"])

    prompt = "Buy 100000 SHIB with ETH"
    balance = manager.balance_of(shib_address)
    assert balance == 0
    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(shib_address)

    expected_amount = 100000
    expected_amount_plus_slippage = expected_amount * PLUS_DIFFERENCE_PERCENTAGE
    assert expected_amount <= new_balance and new_balance <= expected_amount + expected_amount_plus_slippage

def test_auto_tx_swap_native(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])

    prompt = "Buy 100 USDC with ETH"
    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(usdc_address)
    expected_amount = 100
    expected_amount_plus_slippage = expected_amount * PLUS_DIFFERENCE_PERCENTAGE
    assert expected_amount <= new_balance and new_balance <= expected_amount + expected_amount_plus_slippage

def test_auto_tx_swap_multiple_1(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Buy 1000 USDC with ETH and then buy WBTC with 500 USDC"
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)

    expected_amount = 500
    usdc_balance = manager.balance_of(usdc_address)
    expected_amount_plus_slippage = 1000 * PLUS_DIFFERENCE_PERCENTAGE
    assert expected_amount <= usdc_balance and usdc_balance <= expected_amount + expected_amount_plus_slippage
    assert wbtc_balance < manager.balance_of(wbtc_address)

def test_auto_tx_swap_multiple_2(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
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

def test_auto_tx_swap_triple(configuration, auto_tx): 
    (_, _, _, manager) = configuration
    web3 = load_w3()
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
    assert expected_usdc_amount <= usdc_balance and usdc_balance <= expected_usdc_amount + (expected_usdc_amount * PLUS_DIFFERENCE_PERCENTAGE)
    assert expected_uni_amount <= uni_balance  and uni_balance <= expected_uni_amount + (expected_uni_amount * PLUS_DIFFERENCE_PERCENTAGE)
    assert expected_wbtc_amount <= wbtc_balance and wbtc_balance <= expected_wbtc_amount + (expected_wbtc_amount * PLUS_DIFFERENCE_PERCENTAGE)

def test_auto_tx_swap_complex_1(configuration, auto_tx): # This one is complex because it confuses the LLM with WBTC amount
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Swap ETH to 0.05 WBTC, then, swap WBTC to 1000 USDC"
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)
    expected_amount = 1000
    usdc_balance = manager.balance_of(usdc_address)
    expected_amount_plus_slippage = expected_amount * PLUS_DIFFERENCE_PERCENTAGE
    assert expected_amount <= usdc_balance and usdc_balance <= expected_amount + expected_amount_plus_slippage
    assert wbtc_balance < manager.balance_of(wbtc_address)

def test_auto_tx_swap_complex_2(configuration, auto_tx): # This one is complex because it confuses the LLM with WBTC amount
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = NetworkInfo(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"])
    wbtc_address = ETHAddress(network_info.tokens["wbtc"])

    prompt = "Buy 1000 USDC with ETH, then sell the USDC to buy 0.001 WBTC"
    usdc_balance = manager.balance_of(usdc_address)

    auto_tx.run(prompt, non_interactive=True)

    wbtc_balance = manager.balance_of(wbtc_address)
    expected_wbtc_amount = 0.001
    expected_wbtc_amount_plus_slippage = (
        expected_wbtc_amount + expected_wbtc_amount * PLUS_DIFFERENCE_PERCENTAGE
    )
    assert expected_wbtc_amount <= wbtc_balance <= expected_wbtc_amount_plus_slippage
    assert usdc_balance < manager.balance_of(usdc_address)
