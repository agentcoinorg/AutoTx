from typing import Any, Optional, cast
import re
import logging

from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3
from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.multicall import Multicall
from gnosis.safe import Safe, SafeOperation, SafeTx
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from web3.types import TxParams, TxReceipt
from gnosis.safe.api import TransactionServiceApi
from eth_account.signers.local import LocalAccount

from autotx import models
from autotx.utils.ethereum.get_native_balance import get_native_balance
from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address, save_cached_safe_address
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.is_valid_safe import is_valid_safe
from autotx.utils.ethereum.networks import ChainId
from .deploy_safe_with_create2 import deploy_safe_with_create2
from .deploy_multicall import deploy_multicall
from .get_erc20_balance import get_erc20_balance
from .constants import MULTI_SEND_ADDRESS, GAS_PRICE_MULTIPLIER


# Disable safe warning logs
logging.getLogger('gnosis.safe.safe').setLevel(logging.CRITICAL + 1)

class ExecutionRevertedError(Exception):
    pass

class SafeManager:
    multisend: MultiSend | None = None
    safe_nonce: int | None = None
    gas_multiplier: float | None = GAS_PRICE_MULTIPLIER
    dev_account: LocalAccount | None = None
    network: ChainId | None = None
    transaction_service_url: str | None = None
    address: ETHAddress
    use_tx_service: bool

    def __init__(
        self, 
        client: EthereumClient, 
        agent: LocalAccount, 
        safe: Safe
    ):
        self.client = client
        self.web3 = self.client.w3
        self.agent = agent
        self.safe = safe
        self.use_tx_service = False
        self.safe_nonce = None
        self.address = ETHAddress(safe.address)


    @classmethod
    def deploy_safe(
        cls, 
        client: EthereumClient, 
        dev_account: LocalAccount, 
        agent: LocalAccount, 
        owners: list[str], 
        threshold: int
    ) -> 'SafeManager':
        safe_address = get_cached_safe_address()
        if not safe_address:
            safe_address = deploy_safe_with_create2(client, dev_account, owners, threshold)
            save_cached_safe_address(safe_address)

        manager = cls(client, agent, Safe(Web3.to_checksum_address(safe_address), client))
        manager.dev_account = dev_account

        manager.multisend = MultiSend(client, address=Web3.to_checksum_address(MULTI_SEND_ADDRESS))

        return manager
    
    @classmethod
    def connect(
        cls, 
        client: EthereumClient, 
        safe_address: ETHAddress,
        agent: LocalAccount, 
    ) -> 'SafeManager':
        safe = Safe(Web3.to_checksum_address(safe_address.hex), client)

        manager = cls(client, agent, safe)

        manager.multisend = MultiSend(client, address=Web3.to_checksum_address(MULTI_SEND_ADDRESS))

        return manager
    
    def connect_tx_service(self, network: ChainId, transaction_service_url: str) -> None:
        self.use_tx_service = True
        self.network = network
        self.transaction_service_url = transaction_service_url
    
    def disconnect_tx_service(self) -> None:
        self.use_tx_service = False
        self.network = None
        self.transaction_service_url = None

    def connect_multisend(self, address: ChecksumAddress) -> None:
        self.multisend = MultiSend(self.client, address=address)

    def connect_multicall(self, address: ETHAddress) -> None:
        self.client.multicall = Multicall(self.client, address.hex)

    def deploy_multicall(self) -> None:
        if not self.dev_account:
            raise ValueError("Dev account not set. This function should not be called in production.")
        multicall_addr = deploy_multicall(self.client, self.dev_account)
        self.connect_multicall(multicall_addr)

    def build_multisend_tx(self, txs: list[TxParams], safe_nonce: Optional[int] = None) -> SafeTx:
        if not self.multisend:
            raise Exception("No multisend contract address has been set to SafeManager")

        multisend_txs = [
            MultiSendTx(MultiSendOperation.CALL, str(tx["to"]), tx["value"], tx["data"])
            for tx in txs
        ]
        safe_multisend_data = self.multisend.build_tx_data(multisend_txs)


        safe_tx = self.safe.build_multisig_tx(
            to=str(self.multisend.address),
            value=sum(tx["value"] for tx in txs),
            data=safe_multisend_data,
            operation=SafeOperation.DELEGATE_CALL.value,
            safe_nonce=self.track_nonce(safe_nonce)
        )

        return safe_tx

    def build_tx(self, tx: TxParams, safe_nonce: Optional[int] = None) -> SafeTx:
        safe_tx = SafeTx(
            self.client,
            self.address.hex,
            str(tx["to"]),
            tx["value"],
            cast(bytes, tx["data"]),
            0,
            0,
            0,
            self.gas_price(),
            None,
            self.address.hex,
            safe_nonce=self.track_nonce(safe_nonce),
        )
        safe_tx.safe_tx_gas = self.safe.estimate_tx_gas(safe_tx.to, safe_tx.value, safe_tx.data, safe_tx.operation)
        safe_tx.base_gas = self.safe.estimate_tx_base_gas(safe_tx.to, safe_tx.value, safe_tx.data, safe_tx.operation, NULL_ADDRESS, safe_tx.safe_tx_gas)

        return safe_tx
    
    def execute_tx(self, tx: TxParams, safe_nonce: Optional[int] = None) -> HexBytes:
        if not self.dev_account:
            raise ValueError("Dev account not set. This function should not be called in production.")

        try:
            safe_tx = self.build_tx(tx, safe_nonce)

            safe_tx.sign(self.agent.key.hex())

            safe_tx.call(tx_sender_address=self.dev_account.address)

            tx_hash, _ = safe_tx.execute(
                tx_sender_private_key=self.dev_account.key.hex()
            )

            print(f"Executed safe tx hash: {tx_hash.hex()}")

            return tx_hash
        except Exception as e:
            extracted_message = re.search(r"revert: ([^,]+)", str(e))
            if extracted_message:
                raise ExecutionRevertedError(extracted_message.group(0))
            
            raise Exception("Unknown error executing transaction", e)


    def execute_multisend_tx(self, txs: list[TxParams], safe_nonce: Optional[int] = None) -> HexBytes:
        if not self.dev_account:
            raise ValueError("Dev account not set. This function should not be called in production.")

        safe_tx = self.build_multisend_tx(txs, safe_nonce)

        safe_tx.sign(self.agent.key.hex())

        safe_tx.call(tx_sender_address=self.dev_account.address)

        tx_hash, _ = safe_tx.execute(
            tx_sender_private_key=self.dev_account.key.hex()
        )

        return tx_hash
    
    def post_transaction(self, tx: TxParams, safe_nonce: Optional[int] = None) -> None:
        if not self.network:
            raise Exception("Network not defined for transaction service")

        ts_api = TransactionServiceApi(
            self.network, ethereum_client=self.client, base_url=self.transaction_service_url
        )

        safe_tx = self.build_tx(tx, safe_nonce)
        safe_tx.sign(self.agent.key.hex())

        ts_api.post_transaction(safe_tx)

    def post_multisend_transaction(self, txs: list[TxParams], safe_nonce: Optional[int] = None) -> None:
        if not self.network:
            raise Exception("Network not defined for transaction service")

        ts_api = TransactionServiceApi(
            self.network, ethereum_client=self.client, base_url=self.transaction_service_url
        )

        tx = self.build_multisend_tx(txs, safe_nonce)
        tx.sign(self.agent.key.hex())

        ts_api.post_transaction(tx)

    def send_tx(self, tx: TxParams | dict[str, Any], safe_nonce: Optional[int] = None) -> str | None:
        if self.use_tx_service:
            self.post_transaction(cast(TxParams, tx), safe_nonce)
            return None
        else:
            hash = self.execute_tx(cast(TxParams, tx), safe_nonce)
            return hash.hex()

    def send_tx_batch(self, txs: list[models.Transaction], require_approval: bool, safe_nonce: Optional[int] = None) -> bool | str: # True if sent, False if declined, str if feedback
        print("=" * 50)

        if not txs:
            print("No transactions to send.")
            return True

        start_nonce = self.track_nonce(safe_nonce)

        transactions_info = "\n".join(
            [
                f"{i + 1}. {tx.summary} (nonce: {start_nonce + i})"
                for i, tx in enumerate(txs)
            ]
        )

        print(f"Prepared transactions:\n{transactions_info}")

        if self.use_tx_service:
            if require_approval:
                response = input("Do you want the above transactions to be sent to your smart account?\nRespond (y/n) or write feedback: ")

                if response.lower() == "n" or response.lower() == "no":
                    print("Transactions not sent to your smart account (declined).")
                  
                    self.reset_nonce(start_nonce)
                  
                    return False
                elif response.lower() != "y" and response.lower() != "yes":
                    
                    self.reset_nonce(start_nonce)
                    
                    return response
            else:
                print("Non-interactive mode enabled. Transactions will be sent to your smart account without approval.")

            print("Sending transactions to your smart account...")

            for i, tx in enumerate([prepared_tx.params for prepared_tx in txs]):
                self.send_tx(tx, start_nonce + i)

            print("Transactions sent to your smart account for signing.")
            
            return True
        else:
            if require_approval:
                response = input("Do you want to execute the above transactions?\nRespond (y/n) or write feedback: ")

                if response.lower() == "n" or response.lower() == "no":
                    print("Transactions not executed (declined).")
                    
                    self.reset_nonce(start_nonce)
                    
                    return False
                elif response.lower() != "y" and response.lower() != "yes":
                    
                    self.reset_nonce(start_nonce)
                    
                    return response
            else:
                print("Non-interactive mode enabled. Transactions will be executed without approval.")

            print("Executing transactions...")

            for i, prepared_tx in enumerate([prepared_tx for prepared_tx in txs]):
                try:
                    self.send_tx(prepared_tx.params, start_nonce + i)
                except ExecutionRevertedError as e:
                    raise Exception(f"{prepared_tx.summary} failed with error: {e}")
        
            print("Transactions executed.")

            return True

    def send_empty_tx(self, safe_nonce: Optional[int] = None) -> str | None:
        tx: TxParams = {
            "to": self.address.hex,
            "value": self.web3.to_wei(0, "ether"),
            "data": b"",
            "from": self.address.hex,
        }

        return self.send_tx(tx, safe_nonce)

    def wait(self, tx_hash: HexBytes) -> TxReceipt:
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def balance_of(self, token_address: ETHAddress | None = None) -> float:
        if token_address is None:
            return get_native_balance(self.web3, self.address)
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
    
    def reset_nonce(self, starting_safe_nonce: Optional[int] = None) -> None:
        if starting_safe_nonce is None:
            self.safe_nonce = None
        else:
            self.safe_nonce = starting_safe_nonce - 1 # -1 because it will be incremented in track_nonce

    @staticmethod
    def is_valid_safe(client: EthereumClient, address: ETHAddress) -> bool:
        return is_valid_safe(client, address)
