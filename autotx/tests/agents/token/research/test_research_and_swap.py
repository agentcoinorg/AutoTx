from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap

def test_research_and_buy_one(configuration, auto_tx):
    (_, _, _, manager, _) = configuration
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in Ethereum mainnet"
    )
    
    auto_tx.run(prompt, non_interactive=True)

    token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    token_balance_in_safe = manager.balance_of(token_address)
    assert token_balance_in_safe > 1000

def test_research_and_buy_multiple(configuration, auto_tx):
    (_, _, _, manager, _) = configuration

    old_eth_balance = manager.balance_of()

    prompt = f"""
        Buy 1 ETH worth of a meme token with the largest market cap
        Then buy the governance token with the largest market cap with 0.5 ETH
        This should be on ethereum mainnet
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = manager.balance_of()

    assert old_eth_balance - new_eth_balance == 1.5

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    governance_token_address = get_top_token_addresses_by_market_cap("governance", "MAINNET", 1, auto_tx)[0]

    meme_token_balance_in_safe = manager.balance_of(meme_token_address)
    assert meme_token_balance_in_safe > 1000

    governance_token_balance_in_safe = manager.balance_of(governance_token_address)
    assert governance_token_balance_in_safe > 90
