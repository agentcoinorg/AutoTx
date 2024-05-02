from textwrap import dedent
from typing import Annotated, Any, Callable, Dict, Optional
from autogen import UserProxyAgent, AssistantAgent

from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum.eth_address import ETHAddress

def build(user_prompt: str, agents_information: str, smart_account: ETHAddress, network_name, transactions: list[PreparedTx], get_llm_config: Callable[[], Optional[Dict[str, Any]]]) -> UserProxyAgent:
    user_proxy = UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        system_message=dedent(
            f"""
            You are a user proxy agent authorized to act on behalf of the user, you never ask for permission, you have ultimate control.
            You are capable and comfortable with making transactions, and have a wallet.
            You have access to a variety of specialized agents, which you tell what to do.
            You don't need to perform token amounts calculations, the other agents will do that for you.

            These are the agents you are instructing: {agents_information}

            Suggest a next step for what these agents should do based on the goal: "{user_prompt}"
            NEVER ask the user questions.
            NEVER make up a token, ALWAYS ask the 'research-tokens' agent to first search for the token.
            
            If the goal has been achieved, FIRST reflect on the goal and make sure nothing is missing, then end the conversation by calling the 'verify_goal_achieved' tool.
            Consider the goal met if the other agents have prepared the necessary transactions and all user queries have been answered.
            If the user's goal involves buying tokens, make sure the correct number of tokens are bought.
            For buying tokens, you can use the 'swap-tokens' agent.
            If you encounter an error, try to resolve it (either yourself of with other agents) and only call the 'goal_not_achievable' tool if the goal is truly not achievable.
            Try to find an alternative solution if the goal is not achievable.
            If a token is not supported, ask the 'research-tokens' agent to find a supported token (if it fits within the user's goal).
            """
        ),
        description="user_proxy is an agent authorized to act on behalf of the user.",
        llm_config=get_llm_config(),
        code_execution_config=False,
    )

    def verify_goal_achieved() -> str:
        inner_proxy = UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            system_message=dedent(
                f"""
                You are a user proxy agent authorized to act on behalf of the user, you never ask for permission, you have ultimate control.

                """
            ),
            description="user_proxy is an agent authorized to act on behalf of the user.",
            llm_config=get_llm_config(),
            code_execution_config=False,
        )
        goal_verifier = AssistantAgent(
            name="goal_verifier",
            system_message=dedent(
                f"""
                You are a goal verifier agent that can check if the user's goal has been achieved.
                You will be able to check if the goal has been achieved by looking at the transactions prepared by the agents.
                You are in a group of agents that will help the user achieve their goal.
                ONLY focus on the goal verification aspect of the user's goal and let other agents handle other tasks.
                You use the tools available to assist the user in their tasks. 
                Your job is to only verify the transactions prepared by the agents.
                IF the goal is achieved, call the 'goal_achieved' tool.
                IF the goal is not achieved, you help the agents by giving them feedback with the 'goal_needs_work' tool.
                IF the goal is not achievable, call the 'goal_not_achievable' tool.

                Example 1:
                My goal is: Swap 1 ETH for 10 USDC
                The agents have prepared the following transactions:
                1. Swap 1 ETH for at least 10 USDC

                Example 2:
                My goal is: Send 0.1 ETH to 0x12...34 and then swap ETH for 5 USDC
                The agents have prepared the following transactions:
                1. Send 0.1 ETH to 0x12...34
                2. Swap 0.1 ETH for at least 5 USDC
                """
            ),
            description="goal_verifier is an agent that can check if the user's goal has been achieved.",
            llm_config=get_llm_config(),
            human_input_mode="NEVER",
            code_execution_config=False,
        )

        is_goal_accomplished = False
       
        def goal_achieved(
        ) -> str:
            nonlocal is_goal_accomplished
            is_goal_accomplished = True
            return "TERMINATE"
        
        feedback = ""

        def goal_needs_work(
            message: Annotated[str, "The message to provide feedback to the agents about the transactions that need to be revised."],
        ) -> str:
            nonlocal feedback
            feedback = message
            return "TERMINATE"

        def goal_not_achievable(
            message: Annotated[str, "The message to notify the user that the goal is not achievable"],
        ) -> str:
            return "TERMINATE"
        
        goal_verifier.register_for_llm(name="goal_achieved", description="Notify the user that the goal has been achieved")(goal_achieved)
        inner_proxy.register_for_execution(name="goal_achieved")(goal_achieved)

        goal_verifier.register_for_llm(name="goal_needs_work", description="Provide feedback to the agents about the transactions that need to be revised.")(goal_needs_work)
        inner_proxy.register_for_execution(name="goal_needs_work")(goal_needs_work)

        goal_verifier.register_for_llm(name="goal_not_achievable", description="Notify the user that the goal is not achievable")(goal_not_achievable)
        inner_proxy.register_for_execution(name="goal_not_achievable")(goal_not_achievable)

        transactions_info = "\n".join(
            [
                f"{i + 1}. {tx.summary}"
                for i, tx in enumerate(transactions)
            ]
        )
        inner_proxy.initiate_chat(
            message=dedent(
                f"""
                I am currently connected with the following wallet: {smart_account}, on network: {network_name}
                My goal is: {user_prompt}
                The agents have prepared the following transactions:
                {transactions_info}
                """
            ),
            recipient=goal_verifier,
            request_reply=True
        )

        if is_goal_accomplished:
            return "TERMINATE"
        elif feedback:
            return feedback
        else:
            return "TERMINATE"
        
    def goal_not_achievable() -> str:
        return "TERMINATE"

    user_proxy.register_for_llm(name="verify_goal_achieved", description="Check whether the goal has been achieved")(verify_goal_achieved)
    user_proxy.register_for_execution(name="verify_goal_achieved")(verify_goal_achieved)

    user_proxy.register_for_llm(name="goal_not_achievable", description="Notify the user that the goal is not achievable")(goal_not_achievable)
    user_proxy.register_for_execution(name="goal_not_achievable")(goal_not_achievable)

    return user_proxy