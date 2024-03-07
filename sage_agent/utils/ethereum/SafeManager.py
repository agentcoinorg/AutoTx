from .deploy_safe_with_create2 import deploy_safe_with_create2
from .deploy_multicall import deploy_multicall
from .get_erc20_balance import get_erc20_balance
from .constants import MULTI_SEND_ADDRESS
from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from gnosis.eth.multicall import Multicall
from gnosis.safe import Safe, SafeOperation
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from web3.types import TxParams

class SafeManager:
    def __init__(self, client: EthereumClient, user: Account, agent: Account, safe: Safe):
        self.client = client
        self.web3 = self.client.w3
        self.user = user
        self.agent = agent
        self.safe = safe

    @property
    def address(self) -> str:
        return self.safe.address

    @classmethod
    def deploy_safe(cls, client: EthereumClient, user: Account, agent: Account, owners: list[str], threshold: int):
        safe = deploy_safe_with_create2(client, user, owners, threshold)

        manager = cls(client, user, agent, safe)

        manager.multisend = MultiSend(client, address=MULTI_SEND_ADDRESS)

        return manager

    def connect_multicall(self, address: str):
        self.client.multicall = Multicall(self.client, address)

    def  deploy_multicall(self):
        multicall_addr = deploy_multicall(self.client, self.user)
        self.connect_multicall(multicall_addr)

    def send_tx(self, tx: TxParams):
        return self.send_txs([tx])

    def send_txs(self, txs: list[TxParams]):
        multisend_txs = [
            MultiSendTx(MultiSendOperation.CALL, tx["to"], tx["value"], tx["data"])
            for tx in txs
        ]
        safe_multisend_data = self.multisend.build_tx_data(multisend_txs)

        safe_tx = self.safe.build_multisig_tx(
            to=self.multisend.address,
            value=sum(tx["value"] for tx in txs),
            data=safe_multisend_data,
            operation=SafeOperation.DELEGATE_CALL.value,
        )

        safe_tx.sign(self.agent.key.hex())

        safe_tx.call(tx_sender_address=self.agent.address)

        tx_hash, _ = safe_tx.execute(
            tx_sender_private_key=self.agent.key.hex()
        )

        return tx_hash

    def wait(self, tx_hash: str):
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def balance_of(self, token_address: str | None = None) -> int:
        if token_address is None:
            return self.web3.eth.get_balance(self.address)
        else:
            return get_erc20_balance(self.web3, token_address, self.address)