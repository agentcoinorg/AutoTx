from typing import Any, Callable, TYPE_CHECKING, Coroutine
from autogen import AssistantAgent, UserProxyAgent
if TYPE_CHECKING:
  from autotx.AutoTx import AutoTx

class AutoTxTool:
  name: str
  description: str

  def register_tool(self, autotx: 'AutoTx', agent: AssistantAgent, user_proxy: UserProxyAgent) -> None:
    tool = self.build_tool(autotx)
    # Register the tool signature with the assistant agent.
    agent.register_for_llm(name=self.name, description=self.description)(tool)
    # Register the tool function with the user proxy agent.
    user_proxy.register_for_execution(name=self.name)(tool)

  def build_tool(self, autotx: 'AutoTx') -> Callable[..., Any] | Callable[..., Coroutine[Any, Any, Any]]:
    raise NotImplementedError