from textwrap import dedent
from typing import TYPE_CHECKING, Annotated, Any, Callable, Dict, Optional
from autogen import UserProxyAgent, AssistantAgent, ModelClient

from autotx.utils.color import Color

if TYPE_CHECKING:
    from autotx.AutoTx import CustomModel

def build(user_proxy: UserProxyAgent, agents_information: str, interactive: bool, get_llm_config: Callable[[], Optional[Dict[str, Any]]], notify_user: Callable[[str, Color | None], None], custom_model: Optional['CustomModel']) -> AssistantAgent:
    missing_1 = dedent("""
        If the goal is not clear or missing information, you MUST ask for more information by calling the request_user_input tool.
        Always ensure you have all the information needed to define the goal that can be executed without prior context.
        Analyze the user's initial goal if there is missing information, and ask the user for it. 
        E.g. "Buy ETH" -> "How much ETH do you want to buy and with what token?"
        """ if interactive else "")

    missing_2 = dedent("""
        - Call the request_user_input tool if more information is needed to define the goal.
        """ if interactive else "")
    
    clarifier_agent = AssistantAgent(
        name="clarifier",
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        system_message=dedent(
            f"""
            Clarifier is an assistant that can analyze a user's goal at the start of the conversation and determine if it is within the scope of the agents.
            The user will provide the goal, and the agents are meant to help prepare one or more necessary transactions to accomplish the goal.
            When dealing with Ethereum transactions, assume the following:
                - When the user want to execute transactions he means to prepare the transactions.
                - The agents can also research, discuss, plan actions and advise the user. All of that is in the scope of the agents.

            You must analyze the goal to be executed by the agents.
            If the goal is invalid or outside the scope of the agents, you MUST call the goal_outside_scope tool.
            Only call goal_outside_scope if the goal is outside of the scope of what the agents can do.
            {
                missing_1
            }
            DO NOT make any assumptions about the user's intent or context and ALWAYS take into account the available tools and their descriptions.
            
            The available agents and tools:
            {agents_information}
            The agents can also: 
            - Research 
            - Discuss
            - Plan actions and advise the user
            - Develop purchase strategies
            - Execute transactions
            All of that is within scope of the agents.

            The only things the clarifier should do are:
            {
                missing_2
            }
            - Call the goal_outside_scope tool if the goal is outside the scope of the agents.
            - Nothing
            Perform these actions ONLY in the BEGINNING of the conversation.
            """
        ),
        description="Clarifier is an assistant that can analyze a user's goal at the start of the conversation and determine if it is within the scope of the agents.",
        llm_config=get_llm_config(),
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    if interactive:
        def request_user_input(
            message: Annotated[str, "The message to ask the user for input"],
        ) -> str:
            return input(f"Question: {message}\nYour reply: ")

        clarifier_agent.register_for_llm(name="request_user_input", description="Request user input")(request_user_input)
        user_proxy.register_for_execution(name="request_user_input")(request_user_input)

    def goal_outside_scope(
        message: Annotated[str, "The message return to the user about why the goal is outside of the supported scope"],
    ) -> str:
        notify_user(f"Goal not supported: {message}", "red")
        return "Goal not supported: TERMINATE"
    
    clarifier_agent.register_for_llm(name="goal_outside_scope", description="Notify the user about their goal not being in the scope of the agents")(goal_outside_scope)
    user_proxy.register_for_execution(name="goal_outside_scope")(goal_outside_scope)

    if custom_model:
        clarifier_agent.register_model_client(model_client_cls=custom_model.client, **custom_model.arguments)

    return clarifier_agent