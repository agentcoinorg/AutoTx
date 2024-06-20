from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance
from autotx.utils.ethereum.get_native_balance import get_native_balance

def test_research_and_buy_one(configuration, auto_tx):
    (_, _, client, manager, _) = configuration
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in Ethereum mainnet"
    )
    
    auto_tx.run(prompt, non_interactive=True)

    token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    token_balance_in_safe = get_erc20_balance(client.w3, token_address, manager.address)
    assert token_balance_in_safe > 1000

def test_research_and_buy_multiple(configuration, auto_tx):
    (_, _, client, manager, _) = configuration

    old_eth_balance = get_native_balance(client.w3, manager.address)

    prompt = f"""
        Buy 1 ETH worth of a meme token with the largest market cap
        Then buy the governance token with the largest market cap with 0.5 ETH
        This should be on ethereum mainnet
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = get_native_balance(client.w3, manager.address)

    assert old_eth_balance - new_eth_balance == 1.5

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    governance_token_address = get_top_token_addresses_by_market_cap("governance", "MAINNET", 1, auto_tx)[0]

    meme_token_balance_in_safe = get_erc20_balance(client.w3, meme_token_address, manager.address)
    assert meme_token_balance_in_safe > 1000

    governance_token_balance_in_safe = get_erc20_balance(client.w3, governance_token_address, manager.address)
    assert governance_token_balance_in_safe > 90
