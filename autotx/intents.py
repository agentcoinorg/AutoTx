from abc import abstractmethod
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from typing import Any, Union, cast
from web3.types import TxParams

from web3 import Web3

from autotx.token import Token
from autotx.transactions import SendTransaction, Transaction
from autotx.utils.ethereum.build_transfer_erc20 import build_transfer_erc20
from autotx.utils.ethereum.build_transfer_native import build_transfer_native
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import a_build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.format_amount import format_amount

class IntentType(str, Enum):
    SEND = "send"
    BUY = "buy"
    SELL = "sell"

class IntentBase(BaseModel):
    type: IntentType
    summary: str

    @abstractmethod
    async def build_transactions(self, web3: Web3, network: NetworkInfo, smart_wallet_address: ETHAddress) -> list[Transaction]:
        pass

class SendIntent(IntentBase):
    receiver: str
    token: Token
    amount: float

    @classmethod
    def create(cls, token: Token, amount: float, receiver: ETHAddress) -> 'SendIntent':
        return cls(
            type=IntentType.SEND,
            token=token,
            amount=amount,
            receiver=receiver.original_str,
            summary=f"Transfer {format_amount(amount)} {token.symbol} to {receiver}",
        )
    
    async def build_transactions(self, web3: Web3, network: NetworkInfo, smart_wallet_address: ETHAddress) -> list[Transaction]:
        tx: TxParams

        if self.token.address == NATIVE_TOKEN_ADDRESS:
            tx = build_transfer_native(web3, smart_wallet_address, ETHAddress(self.receiver), self.amount)
        else:
            tx = build_transfer_erc20(web3, ETHAddress(self.token.address), ETHAddress(self.receiver), self.amount, smart_wallet_address)
            
        transactions: list[Transaction] = [
            SendTransaction.create(
                token=self.token,
                amount=self.amount,
                receiver=ETHAddress(self.receiver),
                params=cast(dict[str, Any], tx),
            )
        ]

        return transactions

class BuyIntent(IntentBase):
    from_token: Token
    to_token: Token
    amount: float

    @classmethod
    def create(cls, from_token: Token, to_token: Token, amount: float) -> 'BuyIntent':
        return cls(
            type=IntentType.BUY,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            summary=f"Buy {format_amount(amount)} {to_token.symbol} with {from_token.symbol}",
        )
    
    async def build_transactions(self, web3: Web3, network: NetworkInfo, smart_wallet_address: ETHAddress) -> list[Transaction]:
        transactions = await a_build_swap_transaction(
            web3,
            Decimal(str(self.amount)),
            ETHAddress(self.from_token.address),
            ETHAddress(self.to_token.address),
            smart_wallet_address,
            False,
            network.chain_id
        )

        return transactions

class SellIntent(IntentBase):
    from_token: Token
    to_token: Token
    amount: float

    @classmethod
    def create(cls, from_token: Token, to_token: Token, amount: float) -> 'SellIntent':
        return cls(
            type=IntentType.SELL,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            summary=f"Sell {format_amount(amount)} {from_token.symbol} for {to_token.symbol}",
        )    
    
    async def build_transactions(self, web3: Web3, network: NetworkInfo, smart_wallet_address: ETHAddress) -> list[Transaction]:

        transactions = await a_build_swap_transaction(
            web3,
            Decimal(str(self.amount)),
            ETHAddress(self.from_token.address),
            ETHAddress(self.to_token.address),
            smart_wallet_address,
            True,
            network.chain_id
        )

        return transactions

Intent = Union[SendIntent, BuyIntent, SellIntent]
