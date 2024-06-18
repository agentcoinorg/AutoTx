from types import SimpleNamespace
from typing import Any, Dict, Union, cast
from autogen import ModelClient
from llama_cpp import (
    ChatCompletion,
    ChatCompletionRequestMessage,
    ChatCompletionRequestToolMessage,
    ChatCompletionResponseMessage,
    Completion,
    CreateChatCompletionResponse,
    Llama,
)


class LlamaClient(ModelClient):  # type: ignore
    def __init__(self, config: dict[str, Any], **args: Any):
        self.llm: Llama = args["llm"]
        self.model: str = config["model"]

    def create(self, params: Dict[str, Any]) -> SimpleNamespace:
        sanitized_messages = self._sanitize_chat_completion_messages(
            cast(list[ChatCompletionRequestMessage], params.get("messages"))
        )
        response = self.llm.create_chat_completion(
            messages=sanitized_messages,
            tools=params.get("tools"),
            model=params.get("model"),
        )

        return SimpleNamespace(**{**response, "cost": "0"})  # type: ignore

    def message_retrieval(
        self, response: CreateChatCompletionResponse
    ) -> list[ChatCompletionResponseMessage]:
        choices = response.choices  # type: ignore
        return [choice["message"] for choice in choices]

    def cost(self, _: Union[ChatCompletion, Completion]) -> float:
        return 0.0

    def get_usage(self, _: Union[ChatCompletion, Completion]) -> dict[str, Any]:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost": 0,
            "model": self.model,
        }

    def _sanitize_chat_completion_messages(
        self, messages: list[ChatCompletionRequestMessage]
    ) -> list[ChatCompletionRequestMessage]:
        sanitized_messages: list[ChatCompletionRequestMessage] = []
        for message in messages:
            if "tool_call_id" in message:
                id: str = cast(ChatCompletionRequestToolMessage, message)[
                    "tool_call_id"
                ]

                def get_tool_name(messages, id: str) -> Union[str, None]:  # type: ignore
                    return next(
                        (
                            message["tool_calls"][0]["function"]["name"]
                            for message in messages
                            if "tool_calls" in message
                            and message["tool_calls"][0]["id"] == id
                        ),
                        None,
                    )

                function_name = get_tool_name(messages, id)
                if function_name is None:
                    raise Exception(f"No tool response for this tool call with id {id}")

                sanitized_messages.append(
                    ChatCompletionRequestToolMessage(**message, name=function_name)  # type: ignore
                )

            else:
                sanitized_messages.append(message)

        return sanitized_messages
