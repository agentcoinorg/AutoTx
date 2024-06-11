from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union
from datetime import datetime

class TransactionType(str, Enum):
    SEND = "send"
    APPROVE = "approve"
    SWAP = "swap"

class TransactionBase(BaseModel):
    type: TransactionType
    id: str = Field(default="")
    task_id: str = Field(default="")
    summary: str
    params: dict[str, Any]

class SendTransaction(TransactionBase):
    receiver: str
    token_symbol: str
    token_address: str
    amount: float

    @classmethod
    def create(cls, token_symbol: str, token_address: str, amount: float, receiver: str, params: dict[str, Any]) -> 'SendTransaction':
        return cls(
            type=TransactionType.SEND,
            token_symbol=token_symbol,
            token_address=token_address,
            amount=amount,
            receiver=receiver,
            params=params,
            summary=f"Transfer {amount} {token_symbol} to {receiver}",
        )

class ApproveTransaction(TransactionBase):
    token_symbol: str
    token_address: str
    amount: float
    spender: str

    @classmethod
    def create(cls, token_symbol: str, token_address: str, amount: float, spender: str, params: dict[str, Any]) -> 'ApproveTransaction':
        return cls(
            type=TransactionType.APPROVE,
            token_symbol=token_symbol,
            token_address=token_address,
            amount=amount,
            spender=spender,
            params=params,
            summary=f"Approve {amount} {token_symbol} to {spender}"
        )

class SwapTransaction(TransactionBase):
    from_token_symbol: str
    to_token_symbol: str
    from_token_address: str
    to_token_address: str
    from_amount: float
    to_amount: float

    @classmethod
    def create(cls, from_token_symbol: str, to_token_symbol: str, from_token_address: str, to_token_address: str, from_amount: float, to_amount: float, params: dict[str, Any]) -> 'SwapTransaction':
        return cls(
            type=TransactionType.SWAP,
            from_token_symbol=from_token_symbol,
            to_token_symbol=to_token_symbol,
            from_token_address=from_token_address,
            to_token_address=to_token_address,
            from_amount=from_amount,
            to_amount=to_amount,
            params=params,
            summary=f"Swap {from_amount} {from_token_symbol} for at least {to_amount} {to_token_symbol}"
        )

Transaction = Union[SendTransaction, ApproveTransaction, SwapTransaction]

class Task(BaseModel):
    id: str
    prompt: str
    address: str
    chain_id: int
    created_at: datetime
    updated_at: datetime
    error: str | None
    running: bool
    messages: List[str]
    transactions: List[Transaction]

class App(BaseModel):
    id: str
    name: str
    api_key: str
    allowed: bool

class AppUser(BaseModel):
    id: str
    user_id: str
    agent_address: str
    created_at: datetime
    app_id: str

class ConnectionCreate(BaseModel):
    user_id: str

class TaskCreate(BaseModel):
    prompt: str
    address: Optional[str] = None
    chain_id: Optional[int] = None
    user_id: str

class SendTransactionsParams(BaseModel):
    address: str
    chain_id: int
    user_id: str

class SupportedNetwork(BaseModel):
    name: str
    chain_id: int