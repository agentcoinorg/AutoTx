from web3 import Web3
from autotx import db
from autotx.intents import Intent
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.transactions import TransactionBase

# ApiSmartAccount is a wrapper around other SmartAccounts that allows for hooks to be added to the transaction process
class ApiSmartAccount(SmartAccount):
    wallet: SmartAccount
    tasks: db.TasksRepository
    task_id: str | None

    def __init__(self, web3: Web3, wallet: SmartAccount, tasks: db.TasksRepository, task_id: str | None = None):
        super().__init__(web3, wallet.address)
        self.wallet = wallet
        self.tasks = tasks
        self.task_id = task_id

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        if self.task_id is None:
            raise ValueError("Task ID is required")

        saved_task = self.tasks.get(self.task_id)
        if saved_task is None:
            raise ValueError("Task not found")

        saved_task.intents.extend(intents)
        self.tasks.update(saved_task)

    async def on_intents_ready(self, _intents: list[Intent]) -> bool | str:
        return True
    
    def send_transaction(self, transaction: TransactionBase) -> None:
        self.wallet.send_transaction(transaction)
    
    def send_transactions(self, transactions: list[TransactionBase]) -> None:
        self.wallet.send_transactions(transactions)