from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_erc20_balance import get_erc20_balance

def test_research_and_swap_meme_token(configuration, auto_tx):
    (_, _, _, manager) = configuration
    
    shib_address = ETHAddress(auto_tx.network.tokens["shib"])
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    
    prompt = (
        f"Swap 1 ETH for the meme token with the largest market cap in ethereum mainnet"
    )
    
    auto_tx.run(prompt, non_interactive=True)
    
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe > 1000

def test_research_swap_and_send_governance_token(configuration, auto_tx, test_accounts):
    (_, _, _, manager) = configuration
    web3 = load_w3()
    
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    uni_balance_in_safe = manager.balance_of(uni_address)
    
    assert uni_balance_in_safe == 0
    receiver = test_accounts[0]
    
    prompt = f"Swap 1 ETH for the governance token with the largest market cap in ethereum mainnet and send 100 units of the bought token to {receiver}"
    
    auto_tx.run(prompt, non_interactive=True)
    
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe > 90
    receiver_balance = get_erc20_balance(web3, uni_address, receiver)
    assert receiver_balance == 100

def test_research_and_swap_many_tokens_subjective_simple(configuration, auto_tx):
    (_, _, _, manager) = configuration
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe == 0

    starting_balance = manager.balance_of()

    prompt = f"I want to use 3 ETH to purchase 3 of the best projects in: GameFi, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

    result = auto_tx.run(prompt, non_interactive=True)

    ending_balance = manager.balance_of()

    # Verify the balance is lower by max 3 ETH
    assert starting_balance - ending_balance <= 3
    # Verify there are at least 5 transactions
    assert len(result.transactions) == 3
    # Verify there are only swap transactions
    assert all([tx.summary.startswith("Swap") for tx in result.transactions])
    # Verify the tokens are different
    assert len(set([tx.summary.split(" ")[-1] for tx in result.transactions])) == 3

def test_research_and_swap_many_tokens_subjective_complex(configuration, auto_tx):
    (_, _, _, manager) = configuration
    uni_address = ETHAddress(auto_tx.network.tokens["uni"])
    
    uni_balance_in_safe = manager.balance_of(uni_address)
    assert uni_balance_in_safe == 0

    starting_balance = manager.balance_of()

    prompt = f"I want to use 3 ETH to purchase 10 of the best projects in: GameFi, NFTs, ZK, AI, and MEMEs. Please research the top projects, come up with a strategy, and purchase the tokens that look most promising. All of this should be on ETH mainnet."

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