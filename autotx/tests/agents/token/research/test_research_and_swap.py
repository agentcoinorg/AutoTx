import pytest

from autotx.tests.agents.token.research.test_research import get_top_token_addresses_by_market_cap
from autotx.tests.conftest import FAST_TEST_TIMEOUT_SEC, SLOW_TEST_TIMEOUT_SEC
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance
from autotx.utils.ethereum.get_native_balance import get_native_balance

@pytest.mark.timeout(FAST_TEST_TIMEOUT_SEC)
def test_research_and_buy_one(smart_account, auto_tx):
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in Ethereum mainnet"
    )
    
    auto_tx.run(prompt, non_interactive=True)

    token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    token_balance_in_safe = get_erc20_balance(smart_account.web3, token_address, smart_account.address)
    assert token_balance_in_safe > 1000

@pytest.mark.timeout(SLOW_TEST_TIMEOUT_SEC)
def test_research_and_buy_multiple(smart_account, auto_tx):

    old_eth_balance = get_native_balance(smart_account.web3, smart_account.address)

    prompt = f"""
        Buy 1 ETH worth of a meme token with the largest market cap
        Then buy the governance token with the largest market cap with 0.5 ETH
        This should be on ethereum mainnet
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = get_native_balance(smart_account.web3, smart_account.address)

    assert old_eth_balance - new_eth_balance == 1.5

    meme_token_address = get_top_token_addresses_by_market_cap("meme-token", "MAINNET", 1, auto_tx)[0]

    governance_token_address = get_top_token_addresses_by_market_cap("governance", "MAINNET", 1, auto_tx)[0]

    meme_token_balance_in_safe = get_erc20_balance(smart_account.web3, meme_token_address, smart_account.address)
    assert meme_token_balance_in_safe > 1000

    governance_token_balance_in_safe = get_erc20_balance(smart_account.web3, governance_token_address, smart_account.address)
    assert governance_token_balance_in_safe > 90
