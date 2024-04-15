from autotx.utils.ethereum import get_erc20_balance, transfer_erc20
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.swap_from_eoa import swap
from autotx.utils.ethereum.networks import NetworkInfo
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient


def fill_dev_account_with_erc20(
    client: EthereumClient,
    dev_account: LocalAccount,
    safe_address: ETHAddress,
    network_info: NetworkInfo,
) -> None:
    tokens_to_transfer = {"usdc": 3500, "dai": 3500, "wbtc": 0.1}
    eth_address = ETHAddress(network_info.tokens["eth"], client.w3)
    for token in network_info.tokens:
        if token in tokens_to_transfer:
            token_address = ETHAddress(network_info.tokens[token], client.w3)
            amount = tokens_to_transfer[token]
            current_balance = get_erc20_balance(client.w3, token_address, safe_address)
            if current_balance < amount:
                swap(
                    client,
                    dev_account,
                    tokens_to_transfer[token],
                    eth_address,
                    ETHAddress(network_info.tokens[token], client.w3),
                )
                transfer_erc20(
                    client.w3, token_address, dev_account, safe_address, amount
                )
