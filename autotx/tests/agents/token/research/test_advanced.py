from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap
from autotx.utils.ethereum.eth_address import ETHAddress

def test_research_and_swap_many_tokens_subjective_simple(configuration, auto_tx):
    (_, _, _, manager, _) = configuration
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe == 0

    starting_balance = manager.balance_of()

    prompt = f"I want to use 3 ETH to purchase 3 of the best projects in: GameFi, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

    result = auto_tx.run(prompt, non_interactive=True)

    ending_balance = manager.balance_of()

    gaming_token_address = get_top_token_addresses_by_market_cap("gaming", "MAINNET", 1, auto_tx)[0]
    gaming_token_balance_in_safe = manager.balance_of(gaming_token_address)

    ai_token_address = get_top_token_addresses_by_market_cap("artificial-intelligence", "MAINNET", 1, auto_tx)[0]
    ai_token_balance_in_safe = manager.balance_of(ai_token_address)

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]
    meme_token_balance_in_safe = manager.balance_of(meme_token_address)

    # Verify the balance is lower by max 3 ETH
    assert starting_balance - ending_balance <= 3
    # Verify there are at least 3 transactions
    assert len(result.transactions) == 3
    # Verify there are only swap transactions
    assert all([tx.summary.startswith("Swap") for tx in result.transactions])
    # Verify the tokens are different
    assert len(set([tx.summary.split(" ")[-1] for tx in result.transactions])) == 3

    # Verify the tokens are in the safe
    assert gaming_token_balance_in_safe > 0
    assert ai_token_balance_in_safe > 0
    assert meme_token_balance_in_safe > 0

def test_research_and_swap_many_tokens_subjective_complex(configuration, auto_tx):
    (_, _, _, manager, _) = configuration

    starting_balance = manager.balance_of()

    prompt = f"I want to use 3 ETH to purchase exactly 10 of the best projects in: GameFi, NFTs, ZK, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

    result = auto_tx.run(prompt, non_interactive=True)

    ending_balance = manager.balance_of()

    # Verify the balance is lower by max 3 ETH
    assert starting_balance - ending_balance <= 3
    # Verify there are at least 5 transactions
    assert len(result.transactions) == 10
    # Verify there are only swap transactions
    assert all([tx.summary.startswith("Swap") for tx in result.transactions])
    # Verify the tokens are different
    assert len(set([tx.summary.split(" ")[-1] for tx in result.transactions])) == 10
