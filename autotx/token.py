from pydantic import BaseModel

class Token(BaseModel):
    symbol: str
    address: str