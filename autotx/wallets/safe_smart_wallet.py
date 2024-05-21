from autotx import models
from autotx.utils.ethereum import SafeManager
from autotx.wallets.smart_wallet import SmartWallet


class SafeSmartWallet(SmartWallet):
    manager: SafeManager
    interactive: bool

    def __init__(self, manager: SafeManager, interactive: bool):
        super().__init__(manager.address)

        self.manager = manager
        self.interactive = interactive

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        pass

    def on_transactions_ready(self, txs: list[models.Transaction]) -> bool | str:
        return self.manager.send_tx_batch(txs, self.interactive)