from pydantic import ConfigDict, Field
from crewai_tools import BaseTool
from autotx.AutoTx import AutoTx

class AutoTxTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    autotx: AutoTx = Field(None)

    def __init__(self, autotx: AutoTx):
        super().__init__()
        self.autotx = autotx