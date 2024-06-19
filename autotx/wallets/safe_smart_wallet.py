from autotx.intents import Intent
from autotx.transactions import TransactionBase
from autotx.utils.ethereum import SafeManager
from autotx.wallets.smart_wallet import SmartWallet


class SafeSmartWallet(SmartWallet):
    manager: SafeManager
    auto_submit_tx: bool

    def __init__(self, manager: SafeManager, auto_submit_tx: bool):
        super().__init__(manager.client.w3, manager.address)

        self.manager = manager
        self.auto_submit_tx = auto_submit_tx

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        pass

    async def on_intents_ready(self, intents: list[Intent]) -> bool | str:
        transactions: list[TransactionBase] = []

        for intent in intents:
            transactions.extend(await intent.build_transactions(self.manager.web3, self.manager.network, self.manager.address))

        return self.manager.send_multisend_tx_batch(transactions, not self.auto_submit_tx)
