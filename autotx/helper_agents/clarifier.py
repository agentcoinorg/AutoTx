from textwrap import dedent
from typing import Annotated, Callable
from autogen import UserProxyAgent, AssistantAgent, Agent as AutogenAgent
from termcolor import cprint

def build(user_proxy: UserProxyAgent, agents_information: str, smart_account_addr: str, network_name: str, not_interactive: bool, get_llm_config: Callable[[],dict]) -> AutogenAgent:
    missing_1 = dedent("""
        If the goal is not clear or missing information, you MUST ask for more information by calling the request_user_input tool.
        Always ensure you have all the information needed to define the goal that can be executed without prior context.
        """ if not not_interactive else "")

    missing_2 = dedent("""
        Analyze the user's initial goal if there is missing information, and ask the user for it. 
        E.g. "Buy ETH" -> "How much ETH do you want to buy and with what token?"
        """ if not not_interactive else "" )
    
    clarifier_agent = AssistantAgent(
        name="clarifier",
        system_message=dedent(
            f"""
            Clarifier is an assistant that helps the user define goals and tasks for your agents. 
            You can analyze goals and provide the user with a goal to be executed by the agents.
            The user will provide the goal, and the agents are meant to help prepare one or more necessary transactions to accomplish the goal.
            When dealing with Ethereum transactions, assume the following:
                - The user's address: {smart_account_addr}
                - The network to interact with: {network_name} 

            You must analyze the goal to be executed by the agents.
            If the goal is invalid or outside the scope of the agents, you MUST call the goal_outside_domain tool.
            Only call goal_outside_domain if the goal is outside of the domain of the agents.
            {
                missing_1
            }
            DO NOT make any assumptions about the user's intent or context and ALWAYS take into account the available tools and their descriptions.
            
            The available agents and tools:
            {agents_information}
            {
                missing_2
            }
            """
        ),
        llm_config=get_llm_config(),
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    if not not_interactive:
        def request_user_input(
            message: Annotated[str, "The message to ask the user for input"],
        ) -> str:
            return input(f"Question: {message}\nYour reply: ")

        clarifier_agent.register_for_llm(name="request_user_input", description="Request user input")(request_user_input)
        user_proxy.register_for_execution(name="request_user_input")(request_user_input)

    def goal_outside_domain(
        message: Annotated[str, "The message return to the user about why the goal is outside of the supported domain"],
    ) -> str:
        cprint(f"Goal not supported: {message}", "red")
        return "TERMINATE"
    
    clarifier_agent.register_for_llm(name="goal_outside_domain", description="Notify the user about their goal not being in the domain of the agents")(goal_outside_domain)
    user_proxy.register_for_execution(name="goal_outside_domain")(goal_outside_domain)
    
    # def goal_supported() -> None:
    #     pass

    # clarifier_agent.register_for_llm(name="goal_supported", description="Call to continue with the solution")(goal_supported)
    # user_proxy.register_for_execution(name="goal_supported")(goal_supported)

    return clarifier_agent