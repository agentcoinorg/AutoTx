from enum import Enum
from pydantic import BaseModel
from typing import Any, List, Optional, Union
from datetime import datetime

class TransactionType(str, Enum):
    SEND = "send"
    APPROVE = "approve"
    SWAP = "swap"

class TransactionBase(BaseModel):
    type: TransactionType
    id: str
    task_id: str
    summary: str
    params: dict[str, Any]

class SendTransaction(TransactionBase):
    type: TransactionType = TransactionType.SEND
    receiver: str
    token_symbol: str
    token_address: str
    amount: float

    def __init__(self, token_symbol: str, token_address: str, amount: float, receiver: str, params: dict[str, Any]):
        super().__init__(
            id="",
            task_id="",
            token_symbol=token_symbol,
            token_address=token_address,
            amount=amount,
            receiver=receiver,
            params=params,
            summary=f"Transfer {amount} {token_symbol} to {receiver}",
        )

class ApproveTransaction(TransactionBase):
    type: TransactionType = TransactionType.APPROVE
    token_symbol: str
    token_address: str
    amount: float
    spender: str

    def __init__(self, token_symbol: str, token_address: str, amount: float, spender: str, params: dict[str, Any]):
        super().__init__(
            id="",
            task_id="",
            token_symbol=token_symbol,
            token_address=token_address,
            amount=amount,
            spender=spender,
            params=params,
            summary=f"Approve {amount} {token_symbol} to {spender}"
        )

class SwapTransaction(TransactionBase):
    type: TransactionType = TransactionType.SWAP
    from_token_symbol: str
    to_token_symbol: str
    from_token_address: str
    to_token_address: str
    from_amount: float
    to_amount: float

    def __init__(self, from_token_symbol: str, to_token_symbol: str, from_token_address: str, to_token_address: str, from_amount: float, to_amount: float, params: dict[str, Any]):
        super().__init__(
            id="",
            task_id="",
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

class TaskCreate(BaseModel):
    prompt: str
    address: Optional[str] = None

class Task(BaseModel):
    id: str
    prompt: str
    created_at: datetime
    updated_at: datetime
    running: bool
    messages: List[str]
    transactions: List[Transaction]

