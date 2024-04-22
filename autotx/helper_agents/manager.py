from textwrap import dedent
from typing import Any, Callable, Dict, Optional
from autogen import GroupChat, GroupChatManager, Agent as AutogenAgent

def build(agents: list[AutogenAgent], max_rounds: int, get_llm_config: Callable[[], Optional[Dict[str, Any]]]) -> AutogenAgent:
    groupchat = GroupChat(
        agents=agents, 
        messages=[], 
        max_round=max_rounds,
        select_speaker_prompt_template = dedent(
            """
            Read the above conversation. Then select the next role from {agentlist} to play. Only return the role and NOTHING else.
            If other roles are trying to communicate with the user, or requesting approval, return the 'user_proxy' role.
            ALWAYS choose the 'clarifier' role first in the conversation.
            Once the roles are ready to execute transactions, choose the 'user_proxy' role.
            If the 'user_proxy' role wants to do something, choose the appropriate role that can help the 'user_proxy' role.
            """
        )
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())

    return manager