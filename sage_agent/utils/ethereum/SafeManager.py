from typing import Optional
from .deploy_safe_with_create2 import deploy_safe_with_create2
from .deploy_multicall import deploy_multicall
from .get_erc20_balance import get_erc20_balance
from .constants import MULTI_SEND_ADDRESS, GAS_PRICE_MULTIPLIER
from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient, EthereumNetwork
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.multicall import Multicall
from gnosis.safe import Safe, SafeOperation, SafeTx
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from web3.types import TxParams
from gnosis.safe.api import TransactionServiceApi

class SafeManager:
    multisend: MultiSend | None = None
    safe_nonce: int | None = None
    gas_multiplier: float | None = GAS_PRICE_MULTIPLIER

    def __init__(
        self, 
        client: EthereumClient, 
        user: Account, 
        agent: Account, 
        safe: Safe
    ):
        self.client = client
        self.web3 = self.client.w3
        self.user = user
        self.agent = agent
        self.safe = safe
        self.use_tx_service = False
        self.safe_nonce = None

    @property
    def address(self) -> str:
        return self.safe.address

    @classmethod
    def deploy_safe(
        cls, 
        client: EthereumClient, 
        user: Account, 
        agent: Account, 
        owners: list[str], 
        threshold: int
    ):
        safe = deploy_safe_with_create2(client, user, owners, threshold)

        manager = cls(client, user, agent, safe)

        manager.multisend = MultiSend(client, address=MULTI_SEND_ADDRESS)

        return manager
    
    def connect_tx_service(self, network: EthereumNetwork, transaction_service_url: str):
        self.use_tx_service = True
        self.network = network
        self.transaction_service_url = transaction_service_url
    
    def disconnect_tx_service(self):
        self.use_tx_service = False
        self.network = None
        self.transaction_service_url = None

    def connect_multisend(self, address: str):
        self.multisend = MultiSend(self.client, address=address)

    def connect_multicall(self, address: str):
        self.client.multicall = Multicall(self.client, address)

    def  deploy_multicall(self):
        multicall_addr = deploy_multicall(self.client, self.user)
        self.connect_multicall(multicall_addr)
    
    def build_multisend_tx(self, txs: list[TxParams], safe_nonce: Optional[int] = None) -> SafeTx:
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
            gas_price=self.gas_price(),
            safe_nonce=self.track_nonce(safe_nonce)
        )

        return safe_tx

    def build_tx(self, tx: TxParams, safe_nonce: Optional[int] = None) -> SafeTx:
        safe_tx = SafeTx(
            self.client,
            self.address,
            tx["to"],
            tx["value"],
            tx["data"],
            0,
            0,
            0,
            self.gas_price(),
            None,
            self.address,
            safe_nonce=self.track_nonce(safe_nonce),
        )
        safe_tx.safe_tx_gas = self.safe.estimate_tx_gas(safe_tx.to, safe_tx.value, safe_tx.data, safe_tx.operation)
        safe_tx.base_gas = self.safe.estimate_tx_base_gas(safe_tx.to, safe_tx.value, safe_tx.data, safe_tx.operation, NULL_ADDRESS, safe_tx.safe_tx_gas)

        return safe_tx
    
    def execute_tx(self, tx: TxParams, safe_nonce: Optional[int] = None):
        safe_tx = self.build_tx(tx, safe_nonce)

        safe_tx.sign(self.agent.key.hex())

        safe_tx.call(tx_sender_address=self.agent.address)

        tx_hash, _ = safe_tx.execute(
            tx_sender_private_key=self.agent.key.hex()
        )

        print(f"Executed safe tx hash: {tx_hash.hex()}")

        return tx_hash

    def execute_multisend_tx(self, txs: list[TxParams], safe_nonce: Optional[int] = None):
        safe_tx = self.build_multisend_tx(txs, safe_nonce)

        safe_tx.sign(self.agent.key.hex())

        safe_tx.call(tx_sender_address=self.agent.address)

        tx_hash, _ = safe_tx.execute(
            tx_sender_private_key=self.agent.key.hex()
        )

        return tx_hash
    
    def post_transaction(self, tx: TxParams, safe_nonce: Optional[int] = None):
        ts_api = TransactionServiceApi(
            self.network, ethereum_client=self.client, base_url=self.transaction_service_url
        )

        safe_tx = self.build_tx(tx, safe_nonce)
        safe_tx.sign(self.agent.key.hex())

        ts_api.post_transaction(safe_tx)
    
    def post_multisend_transaction(self, txs: list[TxParams], safe_nonce: Optional[int] = None):
        ts_api = TransactionServiceApi(
            self.network, ethereum_client=self.client, base_url=self.transaction_service_url
        )

        tx = self.build_multisend_tx(txs, safe_nonce)
        tx.sign(self.agent.key.hex())

        ts_api.post_transaction(tx)

    def send_tx(self, tx: TxParams, safe_nonce: Optional[int] = None) -> str | None:
        if self.use_tx_service:
            self.post_transaction(tx, safe_nonce)
            return None
        else:
            hash = self.execute_tx(tx, safe_nonce)
            return hash.hex()

    def send_multisend_tx(self, txs: list[TxParams], safe_nonce: Optional[int] = None):
        if self.use_tx_service:
            self.post_multisend_transaction(txs, safe_nonce)
            return None
        else:
            return self.execute_multisend_tx(txs, safe_nonce)
        
    def send_empty_tx(self, safe_nonce: Optional[int] = None):
        tx: TxParams = {
            "to": self.address,
            "value": self.web3.to_wei(0, "ether"),
            "data": b"",
            "from": self.address,
        }

        return self.send_tx(tx, safe_nonce)

    def wait(self, tx_hash: str):
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def balance_of(self, token_address: str | None = None) -> int:
        if token_address is None:
            return self.web3.eth.get_balance(self.address)
        else:
            return get_erc20_balance(self.web3, token_address, self.address)
        
    def nonce(self) -> int:
        return self.safe.retrieve_nonce()
    
    def gas_price(self) -> int:
        return self.web3.eth.gas_price if self.gas_multiplier is None else int(self.web3.eth.gas_price * self.gas_multiplier)

    def track_nonce(self, safe_nonce: Optional[int] = None) -> int:
        if safe_nonce is None:
            if self.safe_nonce is None:
                self.safe_nonce = self.nonce()
            else:
                self.safe_nonce += 1
            return self.safe_nonce
        else:
            return safe_nonce