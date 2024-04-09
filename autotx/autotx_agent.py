from typing import Any, Callable, Dict, Optional, TYPE_CHECKING, Self
import autogen
if TYPE_CHECKING:
    from autotx.autotx_tool import AutoTxTool
    from autotx.AutoTx import AutoTx

class AutoTxAgent():
    name: str
    system_message: str | Callable[['AutoTx'], str]
    tools: list['AutoTxTool']
    tool_descriptions: list[str]

    def __init__(self) -> Self:
        self.tool_descriptions = [
            f"{tool.name}: {tool.description}" for tool in self.tools
        ]

    def build_autogen_agent(self, autotx: 'AutoTx', user_proxy: autogen.UserProxyAgent, llm_config: Optional[Dict[str, Any]]) -> autogen.Agent:
        system_message = None
        if isinstance(self.system_message, str):
            system_message = self.system_message
        else:
            get_system_message = self.system_message.__func__
            system_message = get_system_message(autotx)
        
        agent = autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
        )

        for tool in self.tools:
            tool.register_tool(autotx, agent, user_proxy)

        return agent