from dotenv import load_dotenv
from eth_account import Account

from autotx.utils.ethereum.cached_safe_address import delete_cached_safe_address
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction

load_dotenv()

import pytest
from autotx.agents import SendTokensAgent
from autotx.agents import SwapTokensAgent
from autotx.AutoTx import AutoTx
from autotx.chain_fork import stop, start
from autotx.utils.configuration import get_configuration
from autotx.utils.ethereum import (
    SafeManager,
    send_eth,
    transfer_erc20,
)
from gnosis.eth import EthereumClient

@pytest.fixture(autouse=True)
def start_and_stop_local_fork():
    start()

    yield

    stop()

@pytest.fixture()
def configuration():
    (_, agent, client) = get_configuration()
    dev_account = get_dev_account()
    delete_cached_safe_address()

    manager = SafeManager.deploy_safe(
        client, dev_account, agent, [dev_account.address, agent.address], 1
    )

    # Send 10 ETH to the smart account for tests
    send_eth(dev_account, manager.address, 10, client.w3)

    return (dev_account, agent, client, manager)

@pytest.fixture()
def auto_tx(configuration):
    (_, _, client, manager) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)

    return AutoTx(manager, network_info, [
        SendTokensAgent.build_agent_factory(),
        SwapTokensAgent.build_agent_factory(client, manager.address)
    ], None)

@pytest.fixture()
def usdc(configuration) -> ETHAddress:
    (user, _, client, manager) = configuration
 
    chain_id = client.w3.eth.chain_id
    network_info = NetworkInfo(chain_id)
    
    eth_address = ETHAddress(network_info.tokens["eth"], client.w3)
    usdc_address = ETHAddress(network_info.tokens["usdc"], client.w3)

    amount = 100

    swap(client, user, amount, eth_address, usdc_address)
    
    transfer_erc20(client.w3, usdc_address, user, manager.address, amount)

    return usdc_address

@pytest.fixture()
def test_accounts(configuration) -> list[ETHAddress]:
    (_, _, client, _) = configuration

    # Create 10 random test accounts
    accounts = [ETHAddress(Account.create().address, client.w3) for _ in range(10)]

    return accounts

def swap(client: EthereumClient, user: Account, amount: float, from_token: ETHAddress, to_token: ETHAddress):
    txs = build_swap_transaction(
        client, amount, from_token.hex, to_token.hex, user.address, False
    )

    for i, tx in enumerate(txs):
        transaction = user.sign_transaction(
            {
                **tx.tx,
                "nonce": client.w3.eth.get_transaction_count(user.address),
                "gas": 200000,
            }
        )

        hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

        receipt = client.w3.eth.wait_for_transaction_receipt(hash)

        if receipt["status"] == 0:
            print(f"Transaction #{i} failed ")
            break