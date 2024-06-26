import json
from typing import Sequence
from pydantic import BaseModel


def dump_pydantic_list(items: Sequence[BaseModel]) -> str:
    return json.dumps([json.loads(log.model_dump_json()) for log in items])