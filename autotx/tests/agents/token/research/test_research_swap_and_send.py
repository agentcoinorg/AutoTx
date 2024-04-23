from autotx.utils.ethereum import get_erc20_balance, load_w3
from autotx.utils.ethereum.eth_address import ETHAddress

DIFFERENCE_PERCENTAGE = 0.01

def test_research_buy_one_send_one(configuration, auto_tx, test_accounts):
    (_, _, _, manager) = configuration
    web3 = load_w3()

    receiver = test_accounts[0]
    
    shib_address = ETHAddress(auto_tx.network.tokens["shib"])
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in ethereum mainnet then send it to {receiver}"
    )
    
    auto_tx.run(prompt, non_interactive=True)
    
    shib_balance_in_safe = manager.balance_of(shib_address)

    receiver_balance = get_erc20_balance(web3, shib_address, receiver)
    assert receiver_balance > 10000

    assert shib_balance_in_safe / receiver_balance < DIFFERENCE_PERCENTAGE

def test_research_buy_one_send_multiple(configuration, auto_tx, test_accounts):
    (_, _, _, manager) = configuration
    web3 = load_w3()

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]
    
    shib_address = ETHAddress(auto_tx.network.tokens["shib"])
    shib_balance_in_safe = manager.balance_of(shib_address)
    assert shib_balance_in_safe == 0
    
    prompt = (
        f"Buy 1 ETH worth of a meme token with the largest market cap in ethereum mainnet then 10,000 of it to {receiver_1} and 250 of it to {receiver_2}"
    )
    
    auto_tx.run(prompt, non_interactive=True)
    
    shib_balance_in_safe = manager.balance_of(shib_address)

    receiver_1_balance = get_erc20_balance(web3, shib_address, receiver_1)
    assert receiver_1_balance == 10000

    receiver_2_balance = get_erc20_balance(web3, shib_address, receiver_2)
    assert receiver_2_balance == 250

    assert shib_balance_in_safe > 10000

def test_research_buy_multiple_send_multiple(configuration, auto_tx, test_accounts):
    (_, _, _, manager) = configuration
    web3 = load_w3()

    receiver_1 = test_accounts[0]
    receiver_2 = test_accounts[1]
    
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
        This should be on ethereum mainnet.
        Send all of the meme token to {receiver_1} and all of the governance token to {receiver_2}
        """
    
    auto_tx.run(prompt, non_interactive=True)
    
    new_eth_balance = manager.balance_of()

    assert old_eth_balance - new_eth_balance == 1.5

    shib_balance = get_erc20_balance(web3, shib_address, receiver_1)
    assert shib_balance > 10000

    uni_balance = get_erc20_balance(web3, uni_address, receiver_2)
    assert uni_balance > 90

    assert shib_balance_in_safe / shib_balance < DIFFERENCE_PERCENTAGE
    assert uni_balance_in_safe / uni_balance < DIFFERENCE_PERCENTAGE
