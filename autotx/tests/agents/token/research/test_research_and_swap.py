from autotx.utils.ethereum.eth_address import ETHAddress

def test_research_and_buy_one(configuration, auto_tx):
    (_, _, _, manager) = configuration
    
    shib_address = ETHAddress(auto_tx.network.tokens["shib"])
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in ethereum mainnet"
    )
    
    auto_tx.run(prompt, non_interactive=True)
    
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe > 1000

def test_research_and_buy_multiple(configuration, auto_tx):
    (_, _, _, manager) = configuration
    
    shib_address = ETHAddress(auto_tx.network.tokens["shib"])
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe == 0

    old_eth_balance = manager.balance_of()

    prompt = f"""
        Buy 1 ETH worth of a meme token with the largest market cap
        Then buy the governance token with the largest market cap with 0.5 ETH
        This should be on ethereum mainnet
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = manager.balance_of()

    assert old_eth_balance - new_eth_balance == 1.5

    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe > 1000

    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe > 90
