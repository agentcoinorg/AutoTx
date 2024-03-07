from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from gnosis.eth.oracles.abis.uniswap_v3 import uniswap_v3_pool_abi
from gnosis.eth.oracles.uniswap_v3 import UniswapV3Oracle
from sage_agent.get_env_vars import get_env_vars
from sage_agent.utils.ethereum import (
    SafeManager,
    generate_agent_account,
    send_eth,
)

from web3.contract.contract import Contract

from web3.types import TxParams

from sage_agent.utils.ethereum.constants import GAS_PRICE_MULTIPLIER, ROUTER_ADDRESS
from sage_agent.utils.ethereum.mock_erc20 import MOCK_ERC20_ABI

weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
wbtc_address = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

fee = 3000  # 0.3%
slippage = 0.01

sqrt_price_limit = 0


def get_swap_information(
    amount: int, token_in: Contract, token_out: Contract, price: int, exact_input: bool
):
    token_in_decimals = token_in.functions.decimals().call()
    token_out_decimals = token_out.functions.decimals().call()
    if exact_input:
        amount_compared_with_token = amount * price
        minimum_amount_out = int(amount_compared_with_token * 10**token_out_decimals)
        amount_out = int(minimum_amount_out - (minimum_amount_out * slippage))

        return (amount_out, int(amount * 10**token_in_decimals), "exactInputSingle")
    else:
        amount_compared_with_token = amount / price
        max_amount_in = int(amount_compared_with_token * 10**token_in_decimals)
        amount_in = int(max_amount_in + (max_amount_in * slippage))
        return (
            int(amount * 10**token_out_decimals),
            amount_in,
            "exactOutputSingle",
        )


def build_swap_transaction(
    etherem_client: EthereumClient,
    amount: int,
    token_in_address: str,
    token_out_address: str,
    _from: str,
    exact_input: bool,
) -> TxParams:
    uniswap = UniswapV3Oracle(etherem_client, ROUTER_ADDRESS)
    router = uniswap.router
    web3 = etherem_client.w3

    token_in_is_eth = False
    if token_in_address == str(uniswap.weth_address):
        token_in_is_eth = True

    token_in = web3.eth.contract(address=token_in_address, abi=MOCK_ERC20_ABI)
    token_out = web3.eth.contract(address=token_out_address, abi=MOCK_ERC20_ABI)
    price = uniswap.get_price(token_in_address, token_out_address)

    (amount_out, amount_in, method) = get_swap_information(
        amount, token_in, token_out, price, exact_input
    )

    print("Amount in: ", amount_in)
    print("Amount out: ", amount_out)

    transactions: list[TxParams] = []
    if not token_in_is_eth:
        allowance = token_in.functions.allowance(_from, ROUTER_ADDRESS).call()
        if allowance <= amount_in:
            transactions.append(
                token_in.functions.approve(ROUTER_ADDRESS, amount_in).build_transaction(
                    {
                        "from": _from,
                    }
                )
            )

    transactions.append(
        router.functions[method](
            (
                token_in_address,
                token_out_address,
                fee,
                _from,
                amount_out if method == "exactOutputSingle" else amount_in,
                amount_in if method == "exactOutputSingle" else amount_out,
                sqrt_price_limit,
            )
        ).build_transaction({"value": amount_in if token_in_is_eth else 0, "gas": None})
    )

    return transactions


def swap_test():
    rpc_url, user_pk = get_env_vars()
    print("RPC URL: ", rpc_url)

    client = EthereumClient(URI(rpc_url))
    web3 = client.w3

    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    print("User Address: ", user.address)
    print("Agent Address: ", agent.address)

    # 1.- Get safe
    manager = SafeManager.deploy_safe(
        rpc_url, user, agent, [user.address, agent.address], 1
    )
    print("Safe Before Transfer ETH Balance: ", manager.balance_of() / 10**18)

    # send_eth(user, manager.address, int(4 * 10**18), web3)
    # send_eth(user, agent.address, int(4 * 10**18), web3)

    # print("Safe After Transfer ETH Balance: ", manager.balance_of() / 10**18)

    token_out_contract = web3.eth.contract(address=dai_address, abi=MOCK_ERC20_ABI)
    token_out_decimals = token_out_contract.functions.decimals().call()
    balance = token_out_contract.functions.balanceOf(manager.address).call()
    print("Balance of safe before the swap: ", balance / 10**token_out_decimals)

    # 2.- Encode swap transaction
    amount_to_swap = 1000
    encoded_swap: list[TxParams] = build_swap_transaction(
        client, amount_to_swap, usdc_address, dai_address, manager.address, True
    )
    print(encoded_swap)


    # 3.- Execute transaction in safe
    tx_hash = manager.send_txs(encoded_swap)
    manager.wait(tx_hash)
    balance = token_out_contract.functions.balanceOf(manager.address).call()
    print("Safe After Swap ETH Balance: ", manager.balance_of() / 10**18)
    print("Balance of safe after the swap: ", balance / 10**token_out_decimals)
