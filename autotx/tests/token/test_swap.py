from autotx.patch import patch_langchain
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS
from autotx.utils.ethereum.eth_address import ETHAddress

patch_langchain()

def test_auto_tx_swap_eth(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)

    prompt = "Buy 100 USDC with ETH"
    balance = manager.balance_of(usdc_address)

    auto_tx.run(prompt, non_interactive=True)

    new_balance = manager.balance_of(usdc_address)

    assert balance + 100 == new_balance

def test_auto_tx_swap_multiple(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    network_info = SUPPORTED_NETWORKS.get(web3.eth.chain_id)
    usdc_address = ETHAddress(network_info.tokens["usdc"], web3)
    wbtc_address = ETHAddress(network_info.tokens["wbtc"], web3)

    prompt = "Buy 1000 USDC with ETH and then buy WBTC with 500 USDC"
    usdc_balance = manager.balance_of(usdc_address)
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)

    assert usdc_balance + 500 == manager.balance_of(usdc_address)
    assert wbtc_balance < manager.balance_of(wbtc_address)
