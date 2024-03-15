import json
from typing import Dict
from pydantic import RootModel

class ContractsAddresses(RootModel):
    root: Dict[str, Dict[str, str]]

    def __getitem__(self, attr):
        return self.root.get(attr)

    def items(self):
        return self.root.items()

contracts_config: ContractsAddresses = ContractsAddresses.model_validate(
    json.loads(open("autotx/config/addresses.json", "r").read())
)
