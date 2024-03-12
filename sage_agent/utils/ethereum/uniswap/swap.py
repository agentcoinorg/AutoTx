from gnosis.eth import EthereumClient
from gnosis.eth.oracles.uniswap_v3 import UniswapV3Oracle


from web3.contract.contract import Contract

from web3.types import TxParams
from sage_agent.utils.ethereum.constants import GAS_PRICE_MULTIPLIER

from sage_agent.utils.ethereum.mock_erc20 import MOCK_ERC20_ABI


FEE = 3000  # 0.3%
SLIPPAGE = 0.01
SQRT_PRICE_LIMIT = 0


def get_swap_information(
    amount: float, token_in: Contract, token_out: Contract, price: float, exact_input: bool
):
    token_in_decimals = token_in.functions.decimals().call()
    token_out_decimals = token_out.functions.decimals().call()
    if exact_input:
        amount_compared_with_token = amount * price
        minimum_amount_out = int(amount_compared_with_token * 10**token_out_decimals)
        amount_out = int(minimum_amount_out - (minimum_amount_out * SLIPPAGE))
        return (amount_out, int(amount * 10**token_in_decimals), "exactInputSingle")
    else:
        amount_compared_with_token = amount / price
        max_amount_in = int(amount_compared_with_token * 10**token_in_decimals)
        amount_in = int(max_amount_in + (max_amount_in * SLIPPAGE))
        return (
            int(amount * 10**token_out_decimals),
            amount_in,
            "exactOutputSingle",
        )


def build_swap_transaction(
    etherem_client: EthereumClient,
    amount: float,
    token_in_address: str,
    token_out_address: str,
    _from: str,
    exact_input: bool,
) -> list[TxParams]:
    uniswap = UniswapV3Oracle(etherem_client)
    web3 = etherem_client.w3

    token_in_is_eth = token_in_address == str(uniswap.weth_address)

    token_in = web3.eth.contract(address=token_in_address, abi=MOCK_ERC20_ABI)
    token_out = web3.eth.contract(address=token_out_address, abi=MOCK_ERC20_ABI)
    price = uniswap.get_price(token_in_address, token_out_address)

    (amount_out, amount_in, method) = get_swap_information(
        amount, token_in, token_out, price, exact_input
    )

    transactions: list[TxParams] = []
    if not token_in_is_eth:
        allowance = token_in.functions.allowance(_from, uniswap.router_address).call()
        if allowance <= amount_in:
            transactions.append(
                token_in.functions.approve(
                    uniswap.router_address, amount_in
                ).build_transaction(
                    {
                        "from": _from,
                        "gasPrice": int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER),
                    }
                )
            )

    transactions.append(
        uniswap.router.functions[method](
            (
                token_in_address,
                token_out_address,
                FEE,
                _from,
                amount_out if method == "exactOutputSingle" else amount_in,
                amount_in if method == "exactOutputSingle" else amount_out,
                SQRT_PRICE_LIMIT,
            )
        ).build_transaction(
            {
                "value": amount_in if token_in_is_eth else 0,
                "gas": None,
                "gasPrice": int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER),
            }
        )
    )
    return transactions
