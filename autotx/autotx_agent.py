from typing import Any, Callable, Dict, Optional, TYPE_CHECKING, Union
import autogen

from autotx.utils.color import Color
if TYPE_CHECKING:
    from autotx.autotx_tool import AutoTxTool
    from autotx.AutoTx import AutoTx, CustomModel

class AutoTxAgent():
    name: str
    system_message: str | Callable[['AutoTx'], str]
    description: str
    tools: list['AutoTxTool']
    tool_descriptions: list[str]

    def __init__(self) -> None:
        self.tool_descriptions = [
            f"{tool.name}: {tool.description}" for tool in self.tools
        ]

    def build_autogen_agent(self, autotx: 'AutoTx', user_proxy: autogen.UserProxyAgent, llm_config: Optional[Dict[str, Any]], custom_model: Optional['CustomModel'] = None) -> autogen.Agent:
        system_message = None
        if isinstance(self.system_message, str):
            system_message = self.system_message
        else:
            get_system_message = self.system_message.__func__ # type: ignore
            system_message = get_system_message(autotx)
        
        agent = autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            description=self.description,
        )

        # Print all messages sent form the verifier to the group chat manager,
        # as they tend to contain valuable information
        def send_message_hook(
            sender: autogen.AssistantAgent,
            message: Union[Dict[str, Any], str],
            recipient: autogen.Agent,
            silent: bool,
        ) -> Union[Dict[str, Any], str]:
            if recipient.name == "chat_manager" and message != "TERMINATE":
                if isinstance(message, str):
                    autotx.notify_user(message, "light_yellow")
                elif message["content"] != None:
                    autotx.notify_user(message["content"], "light_yellow")
            return message

        agent.register_hook(
            "process_message_before_send",
            send_message_hook
        )

        for tool in self.tools:
            tool.register_tool(autotx, agent, user_proxy)

        if custom_model:
            agent.register_model_client(model_client_cls=custom_model.client, **custom_model.arguments)

        return agent