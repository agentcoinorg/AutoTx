from textwrap import dedent

import pytest
from sage_agent.utils.ethereum import (
    SafeManager,
    build_transfer_erc20,
    get_erc20_balance,
    send_eth,
)
from sage_agent.utils.ethereum.uniswap.swap import build_swap_transaction
from sage_agent.utils.configuration import get_configuration
from sage_agent.utils.ethereum.config import contracts_config
from web3 import Web3

dai_address = contracts_config["erc20"]["dai"]
weth_address = contracts_config["erc20"]["weth"]
usdc_address = contracts_config["erc20"]["usdc"]
wbtc_address = contracts_config["erc20"]["wbtc"]


@pytest.mark.skip()
def test_swap(configuration):
    (user, _, client, _) = configuration

    dai_balance = get_erc20_balance(client.w3, dai_address, user.address)
    usdc_balance = get_erc20_balance(client.w3, usdc_address, user.address)
    wbtc_balance = get_erc20_balance(client.w3, wbtc_address, user.address)
    eth_balance = client.w3.eth.get_balance(user.address)

    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )

    # txs = build_swap_transaction(
    #     client, 3.5, weth_address, usdc_address, user.address, True
    # )

    txs = build_swap_transaction(
        client, 2000, usdc_address, dai_address, user.address, True
    )

    print(txs)

    # for (i, tx) in enumerate(txs):
    transaction = user.sign_transaction(
        {
            **txs[0],
            "nonce": client.w3.eth.get_transaction_count(user.address),
            "gas": 12000000,
        }
    )

    hash = client.w3.eth.send_raw_transaction(transaction.rawTransaction)

    receipt = client.w3.eth.wait_for_transaction_receipt(hash)

    if receipt["status"] == 0:
        print(f"Transaction failed ")
        # break

    dai_balance = get_erc20_balance(client.w3, dai_address, user.address)
    usdc_balance = get_erc20_balance(client.w3, usdc_address, user.address)
    wbtc_balance = get_erc20_balance(client.w3, wbtc_address, user.address)
    eth_balance = client.w3.eth.get_balance(user.address)

    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )


def test_swap_and_through_safe():
    (user, agent, client) = get_configuration()
    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    dai_balance = manager.balance_of(dai_address)
    usdc_balance = manager.balance_of(usdc_address)
    wbtc_balance = manager.balance_of(wbtc_address)
    eth_balance = manager.balance_of(None)

    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )

    # # Send 1 ETH to the agent, so it can execute transactions
    # _ = send_eth(user, agent.address, int(1 * 10**18), client.w3)

    # # Send 4 ETH to the safe, so it can swap
    # _ = send_eth(user, manager.address, int(4 * 10**18), client.w3)

    # Swap 1 ETH to DAI
    txs = build_swap_transaction(
        client, 2000, usdc_address, dai_address, manager.address, True
    )

    # txs = build_swap_transaction(
    #     client, 2000, usdc_address, wbtc_address, manager.address, True
    # )

    # transfer_tx = build_transfer_erc20(
    #     client.w3, usdc_address, "0x61FfE691821291D02E9Ba5D33098ADcee71a3a17", 1800
    # )

    # txs.append(transfer_tx)

    # Swap 5 USDC to dai
    # txs = build_swap_transaction(
    #     client, 5, usdc_address, dai_address, manager.address, True
    # )

    hash = manager.send_txs(txs)
    manager.wait(hash)

    dai_balance = manager.balance_of(dai_address)
    usdc_balance = manager.balance_of(usdc_address)
    wbtc_balance = manager.balance_of(wbtc_address)
    eth_balance = manager.balance_of(None)
    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )
