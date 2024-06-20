import os
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient

from autotx.intents import Intent
from autotx.transactions import TransactionBase
from autotx.utils.ethereum import SafeManager
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.setup import setup_safe
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.agent_account import get_or_create_agent_account
from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address
from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.fill_dev_account_with_tokens import fill_dev_account_with_tokens
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.utils.ethereum.networks import NetworkInfo

class SafeSmartAccount(SmartAccount):
    agent: LocalAccount
    manager: SafeManager
    auto_submit_tx: bool

    def __init__(
        self,
        rpc_url: str,
        network_info: NetworkInfo,
        auto_submit_tx: bool = False,
        smart_account_addr: str | None = None,
        agent: LocalAccount | None = None,
        check_valid_safe: bool = False,
        fill_dev_account: bool = False,
    ):
        client = EthereumClient(URI(rpc_url))

        agent = agent if agent else get_or_create_agent_account()

        smart_account_addr = smart_account_addr if smart_account_addr else os.getenv("SMART_ACCOUNT_ADDRESS")
        smart_account = ETHAddress(smart_account_addr) if smart_account_addr else None
        
        is_safe_deployed = get_cached_safe_address()

        manager = setup_safe(smart_account, agent, client, check_valid_safe)

        if not is_safe_deployed and fill_dev_account:
            fill_dev_account_with_tokens(client.w3, manager.address, network_info)
            print(f"Funds sent to smart account for testing purposes")

        super().__init__(client.w3, manager.address)

        self.manager = manager
        self.agent = agent
        self.auto_submit_tx = auto_submit_tx

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        pass

    async def on_intents_ready(self, intents: list[Intent]) -> bool | str:
        transactions: list[TransactionBase] = []

        for intent in intents:
            transactions.extend(await intent.build_transactions(self.manager.web3, self.manager.network, self.manager.address))

        return self.manager.send_multisend_tx_batch(transactions, not self.auto_submit_tx)

    def send_transaction(self, transaction: TransactionBase) -> None:
        self.manager.send_multisend_tx_batch([transaction], require_approval=False)

    def send_transactions(self, transactions: list[TransactionBase]) -> None:
        self.manager.send_multisend_tx_batch(
            transactions,
            require_approval=False,
        )

