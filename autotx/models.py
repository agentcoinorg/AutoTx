from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime

from autotx.intents import Intent

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
    intents: List[Intent]

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

class BuildTransactionsParams(BaseModel):
    address: str
    chain_id: int
    user_id: str

class SupportedNetwork(BaseModel):
    name: str
    chain_id: int