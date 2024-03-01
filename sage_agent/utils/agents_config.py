import json
from typing import Dict
from pydantic import BaseModel, RootModel


class AgentConfig(BaseModel):
    role: str
    goal: str
    backstory: str


class Agents(RootModel):
    root: Dict[str, AgentConfig]

    def __getitem__(self, attr):
        return self.root.get(attr)


agents_config: Agents = Agents.model_validate(
    json.loads(open("sage_agent/config/agents.json", "r").read())
)
print(agents_config)
