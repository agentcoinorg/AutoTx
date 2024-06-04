from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap
from autotx.utils.ethereum import get_erc20_balance

DIFFERENCE_PERCENTAGE = 0.01

def test_research_buy_one_send_one(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3

    receiver = test_accounts[0]
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in ethereum mainnet then send it to {receiver}"
    )
    
    auto_tx.run(prompt, non_interactive=True)
    
    token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]
    token_balance_in_safe = manager.balance_of(token_address)

    receiver_balance = get_erc20_balance(web3, token_address, receiver)
    assert receiver_balance > 10000

    assert token_balance_in_safe / receiver_balance < DIFFERENCE_PERCENTAGE

def test_research_buy_one_send_multiple(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in ethereum mainnet then 10,000 of it to {receiver_1} and 250 of it to {receiver_2}"
    )
    
    auto_tx.run(prompt, non_interactive=True)

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]
    meme_token_balance_in_safe = manager.balance_of(meme_token_address)

    receiver_1_balance = get_erc20_balance(web3, meme_token_address, receiver_1)
    assert receiver_1_balance == 10000

    receiver_2_balance = get_erc20_balance(web3, meme_token_address, receiver_2)
    assert receiver_2_balance == 250

    assert meme_token_balance_in_safe > 10000

def test_research_buy_multiple_send_multiple(configuration, auto_tx, test_accounts):
    (_, _, client, manager, _) = configuration
    web3 = client.w3

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]

    old_eth_balance = manager.balance_of()

    prompt = f"""
        Buy 1 ETH worth of a meme token with the largest market cap
        Then buy the governance token with the largest market cap with 0.5 ETH
        This should be on ethereum mainnet.
        Send all of the meme token to {receiver_1} and all of the governance token to {receiver_2}
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = manager.balance_of()

    assert old_eth_balance - new_eth_balance == 1.5

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]
    meme_token_balance_in_safe = manager.balance_of(meme_token_address)

    governance_token_address = get_top_token_addresses_by_market_cap("governance", "MAINNET", 1, auto_tx)[0]
    governance_token_balance_in_safe = manager.balance_of(governance_token_address)

    meme_balance = get_erc20_balance(web3, meme_token_address, receiver_1)
    assert meme_balance > 10000

    governance_balance = get_erc20_balance(web3, governance_token_address, receiver_2)
    assert governance_balance > 90

    assert meme_token_balance_in_safe / meme_balance < DIFFERENCE_PERCENTAGE
    assert governance_token_balance_in_safe / governance_balance < DIFFERENCE_PERCENTAGE
