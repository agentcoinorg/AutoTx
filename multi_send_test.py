from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from get_env_vars import get_env_vars
from utils import build_transfer_erc20, build_transfer_eth, deploy_mock_erc20, generate_agent_account, get_erc20_balance, get_eth_balance, send_eth, transfer_erc20
from utils import SafeManager

def multi_send_test():
    rpc_url, user_pk = get_env_vars()

    print("User private key: ", user_pk)
    print("RPC URL: ", rpc_url)

    client = EthereumClient(URI(rpc_url))
    web3 = client.w3
    
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    print("User Address: ", user.address)
    print("Agent Address: ", agent.address)

    _ = send_eth(user, agent.address, 1, web3)
    print("Agent ETH Balance: ", get_eth_balance(agent.address, web3))

    manager = SafeManager.deploy_safe(rpc_url, user, agent, [user.address, agent.address], 1)
    manager.deploy_multicall()
    
    print("Before ETH Balance: ", manager.balance_of())

    _ = send_eth(user, manager.address, 3.1, web3)
    
    print("After ETH Balance: ", manager.balance_of())

    random_address = Account.create().address

    token_address = deploy_mock_erc20(web3, user)

    print("Safe ERC20 before transfer: ", manager.balance_of(token_address))

    transfer_tx = transfer_erc20(web3, token_address, user, manager.address, 100)
    manager.wait(transfer_tx)

    print("Safe ERC20 after transfer: ", manager.balance_of(token_address))

    tx_hash = manager.send_txs([
        build_transfer_erc20(web3, token_address, manager.address, random_address, 5),
        build_transfer_erc20(web3, token_address, manager.address, random_address, 1),
        build_transfer_eth(web3, manager.address, random_address, 1),
        build_transfer_eth(web3, manager.address, random_address, 1),
        build_transfer_eth(web3, manager.address, random_address, 1)
    ])

    manager.wait(tx_hash)

    print("Safe ERC20 after multisend: ", manager.balance_of(token_address))
    print("Random addr ERC20 after multisend: ", get_erc20_balance(web3, token_address, random_address))
    print("Random addr ETH Balance after multisend: ", get_eth_balance(random_address, web3))
