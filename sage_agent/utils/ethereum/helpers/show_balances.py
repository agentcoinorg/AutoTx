from textwrap import dedent

from web3 import Web3

from sage_agent.utils.ethereum import SafeManager, get_erc20_balance
from sage_agent.utils.ethereum.config import contracts_config

dai_address = contracts_config["erc20"]["dai"]
weth_address = contracts_config["erc20"]["weth"]
usdc_address = contracts_config["erc20"]["usdc"]
wbtc_address = contracts_config["erc20"]["wbtc"]


def show_safe_balances(safe: SafeManager):
    dai_balance = safe.balance_of(dai_address)
    usdc_balance = safe.balance_of(usdc_address)
    eth_balance = safe.balance_of(None)
    wbtc_balance = safe.balance_of(wbtc_address)
    weth_balance = safe.balance_of(weth_address)
    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            WETH Balance: {weth_balance / 10 ** 18}
            """
        )
    )


def show_address_balances(web3: Web3, address: str):
    dai_balance = get_erc20_balance(web3, dai_address, address)
    usdc_balance = get_erc20_balance(web3, usdc_address, address)
    wbtc_balance = get_erc20_balance(web3, wbtc_address, address)
    eth_balance = web3.eth.get_balance(address)
    weth_balance = get_erc20_balance(web3, weth_address, address)

    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            WETH Balance: {weth_balance / 10 ** 18}
            """
        )
    )
