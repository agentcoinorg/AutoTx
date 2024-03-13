from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from sage_agent.get_env_vars import get_env_vars
from sage_agent.utils.ethereum import build_transfer_erc20, deploy_mock_erc20, generate_agent_account, get_erc20_balance, get_eth_balance, send_eth, transfer_erc20
from sage_agent.utils.ethereum import SafeManager

def multi_send_test():
    rpc_url, user_pk = get_env_vars()

    print("RPC URL: ", rpc_url)

    client = EthereumClient(URI(rpc_url))
    web3 = client.w3
    
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    print("User Address: ", user.address)
    print("Agent Address: ", agent.address)

    print("User ETH Balance: ", get_eth_balance(web3, user.address))
    print("Agent ETH Balance: ", get_eth_balance(web3, agent.address))

    manager = SafeManager.deploy_safe(rpc_url, user, agent, [user.address, agent.address], 1)
    
    print("Safe Before Transfer ETH Balance: ", manager.balance_of() / 10**18)

    tx_hash, _ = send_eth(user, manager.address, int(0.01 * 10 ** 18), web3)
    tx_hash, _ = send_eth(user, agent.address, int(0.01 * 10 ** 18), web3)

    print("Safe After Transfer ETH Balance: ", manager.balance_of() / 10**18)

    random_address = Account.create().address

    token_address = deploy_mock_erc20(web3, user)

    print("Safe ERC20 before transfer: ", int(manager.balance_of(token_address) / 10**18))

    transfer_tx = transfer_erc20(web3, token_address, user, manager.address, int(100 * 10**18))
    print("Transfer ERC20 TX: ", transfer_tx.hex())
    manager.wait(transfer_tx)

    print("Safe ERC20 after transfer: ", int(manager.balance_of(token_address) / 10**18))

    tx_hash = manager.send_multisend_tx([
        build_transfer_erc20(web3, token_address, random_address, int(4 * 10**18)),
        build_transfer_erc20(web3, token_address, random_address, int(1 * 10**18)),
    ])

    manager.wait(tx_hash)

    print("Random addr", random_address)
    print("Safe ERC20 after multisend: ", int(manager.balance_of(token_address) / 10**18))
    print("Random addr ERC20 after multisend: ", int(get_erc20_balance(web3, token_address, random_address) / 10**18))
    print("Random addr ETH Balance after multisend: ", int(get_eth_balance(web3, random_address) / 10**18))
