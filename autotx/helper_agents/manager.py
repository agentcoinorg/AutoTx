from textwrap import dedent
from typing import Any, Callable, Dict, Optional
from autogen import GroupChat, GroupChatManager, Agent as AutogenAgent

def build(agents: list[AutogenAgent], get_llm_config: Callable[[], Optional[Dict[str, Any]]]) -> AutogenAgent:
    groupchat = GroupChat(
        agents=agents, 
        messages=[], 
        max_round=20,
        select_speaker_prompt_template = dedent(
            """
            Read the above conversation. Then select the next role from {agentlist} to play. Only return the role and NOTHING else.
            If agents are trying to communicate with the user, or requesting approval, return the 'user_proxy' role.
            ALWAYS choose the 'clarifier' role first. If the 'clarifier' asks a question, choose the 'user_proxy' role.
            """
        )
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())

    return manager