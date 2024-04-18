from textwrap import dedent
from typing import Any, Callable, Dict, Optional, Union
from autogen import AssistantAgent, Agent as AutogenAgent
from termcolor import cprint

def build(get_llm_config:Callable[[], Optional[Dict[str, Any]]]) -> AutogenAgent:
    verifier_agent = AssistantAgent(
        name="verifier",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        system_message=dedent(
            """
            Verifier is an expert in verifiying if user goals are met.
            Verifier analyzes chat and responds with TERMINATE if the goal is met.
            Verifier can consider the goal met if the other agents have prepared the necessary transactions.
            Let the other agents complete all the necessary parts of the goal before calling TERMINATE.
            If you find the conversation is repeating and no new progress is made, TERMINATE.
            """
        ),
        description="Verifier is an expert in verifiying if user goals are met.",
        llm_config=get_llm_config(),
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    # Print all messages sent form the verifier to the group chat manager,
    # as they tend to contain valuable information
    def verifier_send_message_hook(
        sender: AssistantAgent,
        message: Union[Dict[str, Any], str],
        recipient: AutogenAgent,
        silent: bool
    ) -> Union[Dict[str, Any], str]:
        if recipient.name == "chat_manager" and message != "TERMINATE":
            if isinstance(message, str):
                cprint(message, "light_yellow")
            elif message["content"] != None:
                cprint(message["content"], "light_yellow")
        return message

    verifier_agent.register_hook(
        "process_message_before_send",
        verifier_send_message_hook
    )

    return verifier_agent