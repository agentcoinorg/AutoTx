import json
import os
from textwrap import dedent
import typing

import openai

from autotx.utils.ethereum.eth_address import ETHAddress

class GoalResponse:
    goal: str
    type: str = "goal"

    def __init__(self, goal: str):
        self.goal = goal

class MissingInfoResponse:
    message: str
    type: str = "missing_info"

    def __init__(self, message: str):
        self.message = message

class InvalidPromptResponse:
    message: str
    type: str = "unsupported"

    def __init__(self, message: str):
        self.message = message

DefineGoalResponse = typing.Union[GoalResponse, MissingInfoResponse, InvalidPromptResponse]

def get_persona(smart_account_address: ETHAddress, current_network: str) -> str:
    return dedent(
        f"""
        You are an AI assistant that helps the user define goals and tasks for your agents. 
        You can analyze prompts and provide the user with a goal to be executed by the agents.
        When dealing with Ethereum transactions, assume the following:
            - The user's address: {smart_account_address}
            - The network to interact with: {current_network} 
        """
    )

def build_goal(prompt: str, agents_information: str, smart_account_address: ETHAddress, current_network: str, non_interactive: bool) -> str:
    response: DefineGoalResponse | None = None
    chat_history = f"User: {prompt}"

    while True:
        response = analyze_user_prompt(chat_history, agents_information, smart_account_address, current_network)
        if response.type == "missing_info":
            autotx_message = f"Missing information: {response.message}"

            if non_interactive:
                raise Exception(autotx_message)
            else:
                chat_history += "\nYou: " + autotx_message + "\nUser: " + input(f"{autotx_message}\nInput response: ")

        elif response.type == "unsupported":
            autotx_message = f"Unsupported prompt: {response.message}"

            if non_interactive:
                raise Exception(autotx_message)
            else:
                chat_history = "User: " + input(f"{autotx_message}\nNew prompt: ")

        elif response.type == "goal":
            return response.goal

def analyze_user_prompt(chat_history: str, agents_information: str, smart_account_address: ETHAddress, current_network: str) -> DefineGoalResponse:
    template = dedent(
        """
        Based on the following chat history between you and the user: 
        ```
        {chat_history}
        ```
            
        You must analyze the prompt and define a goal to be executed by the agents.
        If the prompt is not clear or missing information, you MUST ask for more information.
        If the prompt is invalid, unsupported or outside the scope of the agents, you MUST ask for a new prompt.
        Always ensure you have all the information needed to define the goal that can be executed without prior context.
        DO NOT make any assumptions about the user's intent or context and ALWAYS take into account the available tools and their descriptions.
        
        The available agents and tools:
        {agents_information}

        Respond ONLY in one of three of the following JSON formats:
        1:
        {{
            "type": "goal",
            "goal": "The detailed goal here. No need to mention specific agents or tools. But you MUST mention the user's address."
        }}
        2:
        {{
            "type": "missing_info",
            "message": "The information that is missing here"
        }}
        3:
        {{
            "type": "unsupported",
            "message": "Reason why the prompt is unsupported here"
        }}
        """
    )

    formatted_template = template.format(
        agents_information=agents_information, chat_history=chat_history
    )

    response = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo"),
        response_format={"type": "json_object"},
        messages=[
            { "role": "system", "content": get_persona(smart_account_address, current_network) },
            { "role": "user", "content": formatted_template }
        ],
    )
    response = response.choices[0].message.content
    if not response:
        # TODO: Handle bad response
        pass

    # Only keep the JSON part of the response
    bracket_index = response.find('{')
    bracket_last = response.rfind('}')
    response = response[bracket_index:bracket_last + 1]

    return parse_analyze_prompt_response(response)

def parse_analyze_prompt_response(response: str) -> DefineGoalResponse:
    response = json.loads(response)
    if response["type"] == "goal":
        return GoalResponse(response["goal"])
    elif response["type"] == "missing_info":
        return MissingInfoResponse(response["message"])
    elif response["type"] == "unsupported":
        return InvalidPromptResponse(response["message"])
    else:
        raise Exception("Invalid response type")