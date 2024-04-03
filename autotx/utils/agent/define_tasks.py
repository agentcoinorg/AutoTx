import json
import os
from textwrap import dedent
from crewai import Agent, Task
import openai

def define_tasks(goal: str, agents_information: str, agents: list[Agent]) -> list[Task]:
    template = dedent(
        """
        Based on the following goal: {goal}
            
        You must convert instructions into specific tasks with the following JSON format:
        {{
            tasks : [{{
                "task": "The description of task to be done with details needed given by user. You MUST include the user's address if needed."
                "agent": "The agent that best fits to execute the task"
                "expected_output":"Description of expected output for the task"
                "context": [int] // Index of tasks that will have their output used as context for this task (Always start from 0), if applicable. Eg. [1, 3] or None
                "extra_information": Any extra information as string with description given by the user needed to execute the task, if applicable.
            }}]
        }}

        The specific tasks will be created based on the available agents role, goal and available tools:
        {agents_information}

        IMPORTANT: After all tasks are executed, the prepared transactions will be sent to the Ethereum network.
        """
    )

    formatted_template = template.format(
        agents_information=agents_information, goal=goal
    )

    # TODO: Improve how we pass messages. We should use system role
    response = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo-preview"),
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": formatted_template}],
    )
    response = response.choices[0].message.content
    if not response:
        raise Exception("Bad response from OpenAI API for defining tasks.")

    # Only keep the JSON part of the response
    bracket_index = response.find('{')
    bracket_last = response.rfind('}')
    response = response[bracket_index:bracket_last + 1]

    print("Tasks", response)

    return sanitize_tasks_response(response, agents)

def sanitize_tasks_response(response: str, agents: list[Agent]) -> list[Task]:
    tasks = json.loads(response)["tasks"]
    sanitized_tasks: list[Task] = []
    for task in tasks:
        context: list[Task] = (
            [sanitized_tasks[c] for c in task["context"]] if task["context"] else []
        )

        get_agent_by_name = lambda a: a.name.lower() == task["agent"].lower()
        agent = next(filter(get_agent_by_name, agents), None)
        description = task["task"]
        if not agent:
            raise Exception(f"Agent {task['agent']} not found.", task)

        if task["extra_information"]:
            description += "\n" + task["extra_information"]

        sanitized_tasks.append(
            Task(
                description=description,
                agent=agent,
                expected_output=task["expected_output"],
                context=context,
            )
        )

    return sanitized_tasks