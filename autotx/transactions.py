from enum import Enum
from pydantic import BaseModel
from typing import Any, Union

from autotx.token import Token

class TransactionType(str, Enum):
    SEND = "send"
    APPROVE = "approve"
    SWAP = "swap"

class TransactionBase(BaseModel):
    type: TransactionType
    summary: str
    params: dict[str, Any]

class SendTransaction(TransactionBase):
    receiver: str
    token: Token
    amount: float

    @classmethod
    def create(cls, token: Token, amount: float, receiver: str, params: dict[str, Any]) -> 'SendTransaction':
        return cls(
            type=TransactionType.SEND,
            token=token,
            amount=amount,
            receiver=receiver,
            params=params,
            summary=f"Transfer {amount} {token.symbol} to {receiver}",
        )

class ApproveTransaction(TransactionBase):
    token: Token
    amount: float
    spender: str

    @classmethod
    def create(cls, token: Token, amount: float, spender: str, params: dict[str, Any]) -> 'ApproveTransaction':
        return cls(
            type=TransactionType.APPROVE,
            token=token,
            amount=amount,
            spender=spender,
            params=params,
            summary=f"Approve {amount} {token.symbol} to {spender}"
        )

class SwapTransaction(TransactionBase):
    from_token: Token
    to_token: Token
    from_amount: float
    to_amount: float

    @classmethod
    def create(cls, from_token: Token, to_token: Token, from_amount: float, to_amount: float, params: dict[str, Any]) -> 'SwapTransaction':
        return cls(
            type=TransactionType.SWAP,
            from_token=from_token,
            to_token=to_token,
            from_amount=from_amount,
            to_amount=to_amount,
            params=params,
            summary=f"Swap {from_amount} {from_token.symbol} for at least {to_amount} {to_token.symbol}"
        )

Transaction = Union[SendTransaction, ApproveTransaction, SwapTransaction]
