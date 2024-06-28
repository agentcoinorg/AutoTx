import pytest

from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap
from autotx.eth_address import ETHAddress
from autotx.tests.conftest import MAX_TEST_TIMEOUT_SEC
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance
from autotx.utils.ethereum.get_native_balance import get_native_balance

@pytest.mark.timeout(MAX_TEST_TIMEOUT_SEC)
def test_research_and_swap_many_tokens_subjective_simple(smart_account, auto_tx):
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    
    uni_balance_in_safe = get_erc20_balance(smart_account.web3, uni_address, smart_account.address)
    assert uni_balance_in_safe == 0

    starting_balance = get_native_balance(smart_account.web3, smart_account.address)

    prompt = f"I want to use 3 ETH to purchase 3 of the best projects in: GameFi, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

    result = auto_tx.run(prompt, non_interactive=True)

    ending_balance = get_native_balance(smart_account.web3, smart_account.address)

    gaming_token_address = get_top_token_addresses_by_market_cap("gaming", "MAINNET", 1, auto_tx)[0]
    gaming_token_balance_in_safe = get_erc20_balance(smart_account.web3, gaming_token_address, smart_account.address)

    ai_token_address = get_top_token_addresses_by_market_cap("artificial-intelligence", "MAINNET", 1, auto_tx)[0]
    ai_token_balance_in_safe = get_erc20_balance(smart_account.web3, ai_token_address, smart_account.address)

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]
    meme_token_balance_in_safe = get_erc20_balance(smart_account.web3, meme_token_address, smart_account.address)

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

@pytest.mark.timeout(MAX_TEST_TIMEOUT_SEC)
def test_research_and_swap_many_tokens_subjective_complex(smart_account, auto_tx):

    starting_balance = get_native_balance(smart_account.web3, smart_account.address)

    prompt = f"I want to use 3 ETH to purchase exactly 10 of the best projects in: GameFi, NFTs, ZK, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

    result = auto_tx.run(prompt, non_interactive=True)

    ending_balance = get_native_balance(smart_account.web3, smart_account.address)

    # Verify the balance is lower by max 3 ETH
    assert starting_balance - ending_balance <= 3
    # Verify there are at least 5 transactions
    assert len(result.transactions) == 10
    # Verify there are only swap transactions
    assert all([tx.summary.startswith("Swap") for tx in result.transactions])
    # Verify the tokens are different
    assert len(set([tx.summary.split(" ")[-1] for tx in result.transactions])) == 10
