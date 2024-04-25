from autotx.utils.ethereum import transfer_erc20
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.swap_from_eoa import swap
from autotx.utils.ethereum.networks import ChainId, NetworkInfo
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient

from autotx.utils.ethereum.send_native import send_native


def fill_dev_account_with_tokens(
    client: EthereumClient,
    dev_account: LocalAccount,
    safe_address: ETHAddress,
    network_info: NetworkInfo,
) -> None:
    # XDAI or MATIC doesn't have the same value as ETH, so we need to fill more
    amount_to_fill = 3000 if network_info.chain_id in [ChainId.POLYGON, ChainId.GNOSIS] else 10
    send_native(dev_account, safe_address, amount_to_fill, client.w3)

    tokens_to_transfer = {"usdc": 3500, "dai": 3500, "wbtc": 0.1}
    if network_info.chain_id is ChainId.GNOSIS:
        tokens_to_transfer = {"usdc": 2000, "gno": 5, "cow": 4000 }
    if network_info.chain_id is ChainId.POLYGON:
        tokens_to_transfer = {"usdc": 2000, "wbtc": 0.01, "dai": 2000 }

    native_token_address = ETHAddress(NATIVE_TOKEN_ADDRESS)
    for token in network_info.tokens:
        if token in tokens_to_transfer:
            token_address = ETHAddress(network_info.tokens[token])
            amount = tokens_to_transfer[token]
            swap(
                client,
                dev_account,
                amount,
                native_token_address,
                token_address,
                network_info.chain_id,
            )
            transfer_erc20(client.w3, token_address, dev_account, safe_address, amount)
