from autotx.patch import patch_langchain
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.constants import SUPPORTED_NETWORKS
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

    prompt = "Buy 1000 USDC with ETH and then buy 0.01 WBTC with the USDC"
    usdc_balance = manager.balance_of(usdc_address)
    wbtc_balance = manager.balance_of(wbtc_address)

    auto_tx.run(prompt, non_interactive=True)

    assert usdc_balance + 1000 == manager.balance_of(usdc_address)
    assert wbtc_balance + 0.01 == manager.balance_of(wbtc_address)