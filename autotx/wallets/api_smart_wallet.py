import uuid
from autotx import models
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.wallets.smart_wallet import SmartWallet


class ApiSmartWallet(SmartWallet):
    external_wallet: SmartWallet | None

    def __init__(self, wallet: ETHAddress | SmartWallet, task_id: str, tasks: list[models.Task]):
        super().__init__(wallet.address if isinstance(wallet, SmartWallet) else wallet)
        self.task_id = task_id
        self.tasks = tasks
        if isinstance(wallet, SmartWallet):
            self.external_wallet = wallet
        else:
            self.external_wallet = None

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        saved_task = next(filter(lambda x: x.id == self.task_id, self.tasks), None)
        if saved_task is None:
            raise Exception("Task not found: " + self.task_id)
        for tx in txs:
            tx.id = str(uuid.uuid4())
            tx.task_id = self.task_id

        saved_task.transactions.extend(txs)

        if self.external_wallet:
            self.external_wallet.on_transactions_prepared(txs)

    def on_transactions_ready(self, _txs: list[models.Transaction]) -> bool | str:
        if self.external_wallet:
            return self.external_wallet.on_transactions_ready(_txs)

        return True