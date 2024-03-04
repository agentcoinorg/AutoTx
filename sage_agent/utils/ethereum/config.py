import json
from typing import Dict
from pydantic import BaseModel, RootModel

class ContractsAddresses(RootModel):
    root: Dict[str, Dict[str, str]]

    def __getitem__(self, attr):
        return self.root.get(attr)

    def items(self):
        return self.root.items()

contracts_config: ContractsAddresses = ContractsAddresses.model_validate(
    json.loads(open("sage_agent/config/addresses.json", "r").read())
)
