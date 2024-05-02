
import sys
from textwrap import dedent
from typing import Annotated, Callable, List
from autotx.AutoTx import AutoTx
from autogen import UserProxyAgent

from autotx.agents.InnerResearchTokensAgent import InnerResearchTokensAgent
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool

name = "research-tokens"

system_message = lambda autotx: dedent(f"""
    You are an AI assistant that's an expert in Ethereum tokens. Assist the user in their task of researching tokens.
    ONLY focus on the token research aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks.  
    Your job is NOT to buy or sell a token, and there is no need to check the price when doing that.
    NEVER ask the user questions.
    
    Good examples:
    research: {{ "tasks": "Research USDC token and research DAI token" }}
    research: {{ "tasks": "Find the 24h trading volume of USDC, and what is the largest market cap AI token?" }}
    research: {{ "tasks": "Find the top AI token and top GameFI token, if they're the same find an alternative for one of them" }}
    research: {{ "tasks": "Find the top 3 AI and GameFI tokens. It needs to be exactly 3 tokens without duplicates" }}
    research: {{ "tasks": "Find the top 14 AI and GameFI tokens. It needs to be exactly 14 tokens without duplicates" }}
    research: {{ "tasks": "Retrieve detailed information on the Ethereum token DAI including current price, market cap, and price change percentages." }}
    research: {{ "tasks": "Find all tokens available in the DeFi category and filter them based on their performance on the Optimism network." }}
    research: {{ "tasks": "Compare the price change percentages over the last 24 hours, 7 days, and 30 days for tokens within the Gaming category." }}
    research: {{ "tasks": "Retrieve a list of all available token categories and then research specific details for the first five tokens in the NFT category sorted by volume in descending order." }}
    research: {{ "tasks": "Get the Ethereum addresses for all tokens in the Yield Farming category on the Polygon network to prepare for potential trades." }}

    Bad examples:
    research: {{ "tasks": "Find best crpyto investment strategy" }}
    research: {{ "tasks": "Provide financial advice on which tokens are likely to appreciate in value over the next year." }}
    research: {{ "tasks": "Retrieve the transaction history for a specific Ethereum wallet address." }}
    research: {{ "tasks": "Automatically monitor and alert the user about price changes for a specific token." }}
    research: {{ "tasks": "Analyze the profitability of mining Ethereum tokens." }}

    Only call the research tool once and use multiple tasks if needed. Sometimes it makes more sense to combine tasks if they're related.
    IMPORTANT: When querying for a number of tokens accross multiple categories, make sure to specify the number of tokens and the categories and that there should be no duplicates.
    """
)

description = dedent(
    f"""
    {name} is an AI assistant that's an expert in Ethereum tokens. 
    The agent can also research, discuss, plan actions and advise the user.
    """
)

class ResearchUserQuery(AutoTxTool):
    name: str = "research"
    description: str = "Research user task"

    def build_tool(self, autotx: AutoTx) -> Callable[[str], str]:
        def run(
            tasks: Annotated[str, "User tasks to research"]
        ) -> str:
            print(f"Researching user task:", tasks)

            user_proxy_agent = UserProxyAgent(
                name="user_proxy",
                is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
                human_input_mode="NEVER",
                max_consecutive_auto_reply=10,
                system_message=dedent(
                    f"""
                    You are a user proxy agent authorized to act on behalf of the user, you never ask for permission, you have ultimate control.
                    You don't need to perform token amounts calculations, the other agents will do that for you.
                    NEVER ask the user questions.
                    NEVER make up a token, ALWAYS ask the 'research-tokens' agent to first search for the token.
                    
                    If the goal has been achieved, FIRST reflect on the goal and make sure nothing is missing, then end the conversation with "TERMINATE".
                    Consider the goal met if the other agents have prepared the necessary transactions and all user tasks have been answered.
                    If the user's goal involves buying tokens, make sure the correct number of tokens are bought.
                    If you encounter an error, try to resolve it (either yourself of with other agents) and only respond with "TERMINATE" if the goal is impossible to achieve.
                    If a token is not supported, ask the researcher agent to find a supported token (if it fits within the user's goal).
                    """
                ),
                description="user_proxy is an agent authorized to act on behalf of the user.",
                llm_config=autotx.get_llm_config(),
                code_execution_config=False,
            )
            
            research_agent = InnerResearchTokensAgent().build_autogen_agent(autotx, user_proxy_agent, autotx.get_llm_config())

            chat = user_proxy_agent.initiate_chat(
                research_agent, 
                message=dedent(
                    f"""
                    I am currently connected with the following wallet: {autotx.manager.address}, on network: {autotx.network.chain_id.name}
                    Tasks:
                    {tasks}
                    """
                ), 
                summary_method="reflection_with_llm",
                summary_args={
                    "summary_prompt": dedent(
                        f"""
                        Summarize the answers to the user's tasks.
                        {tasks}
                        """
                    ), 
                }
            )

            print("AAAAAAAAAAAAAAAAAAAAAAAAa")
            print(chat.summary)
            print("BBBBBBBBBBBBBB")

            autotx.current_run_cost_with_cache += float(chat.cost["usage_including_cached_inference"]["total_cost"])
            autotx.current_run_cost_without_cache += float(chat.cost["usage_excluding_cached_inference"]["total_cost"])
            return str(chat.summary)

        return run

class ResearchTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    description = description
    tools = [
        ResearchUserQuery(),
    ]
