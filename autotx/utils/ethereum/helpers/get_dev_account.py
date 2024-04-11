from typing import cast
from eth_account import Account
from eth_account.signers.local import LocalAccount


def get_dev_account() -> LocalAccount:
    return cast(
        LocalAccount,
        Account.from_key(
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        ),
    )
