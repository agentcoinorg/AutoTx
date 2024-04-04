from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import NetworkInfo


def test_auto_tx_research_and_swap(configuration, auto_tx):
    (_, _, client, manager) = configuration
    # web3 = load_w3()
    # network_info = NetworkInfo(web3.eth.chain_id)
    # wbtc_address = ETHAddress(network_info.tokens["wbtc"], web3)

    # receiver = ETHAddress("0x10f8Bf6a479F320ead074411A4b0e7944eA8C9c1", client.w3)

    prompt = f"Swap 1 ETH for the meme token with the largest market cap in ethereum mainnet"

    # wbtc_safe_address = manager.balance_of(wbtc_address)
    # receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    auto_tx.run(prompt, non_interactive=True)

    # new_wbtc_safe_address = manager.balance_of(wbtc_address)
    # new_receiver_wbtc_balance = get_erc20_balance(client.w3, wbtc_address, receiver)

    # assert new_wbtc_safe_address == wbtc_safe_address + 0.04
    # assert new_receiver_wbtc_balance == receiver_wbtc_balance + 0.01