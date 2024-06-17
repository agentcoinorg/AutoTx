from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional
from autogen import GroupChat, GroupChatManager, Agent as AutogenAgent
if TYPE_CHECKING:
    from autotx.AutoTx import CustomModel

def build(agents: list[AutogenAgent], max_rounds: int, interactive: bool, get_llm_config: Callable[[], Optional[Dict[str, Any]]], custom_model: Optional['CustomModel']) -> AutogenAgent:
    clarifier_prompt = "ALWAYS choose the 'clarifier' role first in the conversation." if interactive else ""

    groupchat = GroupChat(
        agents=agents, 
        messages=[], 
        max_round=max_rounds,
        select_speaker_prompt_template = dedent(
            """
            Read the above conversation. Then select the next role from {agentlist} to play.
            If other roles are trying to communicate with the user, or requesting approval, return the 'user_proxy' role.
            """
        ) + dedent(
            f"""{clarifier_prompt}
            Once the roles are ready to execute transactions, choose the 'user_proxy' role.
            If the 'user_proxy' role wants to do something, choose the appropriate role that can help the 'user_proxy' role.
            Only return the role and NOTHING else.
            """
        )
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())
    if custom_model:
        manager.register_model_client(model_client_cls=custom_model.client, **custom_model.arguments)
    return manager