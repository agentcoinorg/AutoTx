from autotx import models
from autotx.utils.ethereum import SafeManager
from autotx.wallets.smart_wallet import SmartWallet


class SafeSmartWallet(SmartWallet):
    manager: SafeManager
    auto_submit_tx: bool

    def __init__(self, manager: SafeManager, auto_submit_tx: bool):
        super().__init__(manager.client.w3, manager.address)

        self.manager = manager
        self.auto_submit_tx = auto_submit_tx

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        pass

    def on_transactions_ready(self, txs: list[models.Transaction]) -> bool | str:
        return self.manager.send_tx_batch(txs, not self.auto_submit_tx)
