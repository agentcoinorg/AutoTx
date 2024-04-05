from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance


def test_auto_tx_research_and_swap_meme_token(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    shib_address = ETHAddress(auto_tx.network.tokens["shib"], web3)
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    prompt = (
        f"Swap 1 ETH for the meme token with the largest market cap in ethereum mainnet"
    )
    auto_tx.run(prompt, non_interactive=True)
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe > 1000


def test_auto_tx_research_swap_and_send_governance_token(configuration, auto_tx):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    uni_address = ETHAddress(auto_tx.network.tokens["uni"], web3)
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe == 0
    receiver = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    prompt = f"Swap 1 ETH for the governance token with the largest market cap in ethereum mainnet and send 100 units of the bought token to {receiver}"
    auto_tx.run(prompt, non_interactive=True)
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe > 90
    receiver_balance = get_erc20_balance(web3, uni_address, receiver)
    assert receiver_balance == 100
