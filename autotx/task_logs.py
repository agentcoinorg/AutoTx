
from datetime import datetime
import json
from typing import Any, Dict, List, Union

from autotx import models

def build_agent_message_log(from_agent: str, to_agent: str, message: Union[Dict[str, Any], str]) -> models.TaskLog:
    return models.TaskLog(
        type="agent-message",
        obj=json.dumps({
            "from": from_agent,
            "to": to_agent,
            "message": message,
        }),
        created_at=datetime.now(),
    )

def format_agent_message_log(obj: Dict[str, Any]) -> Any:
    if type(obj["message"]) == str:
        return f"<b>{obj['from']} -> {obj['to']}:</b>\n{obj['message']}"
    elif type(obj["message"]) == dict:
        obj1 = obj["message"]
        
        if obj1.get("tool_calls") and len(obj1["tool_calls"]) > 0:
            return f"<b>{obj['from']} -> {obj['to']}:</b> <b>*****Tool Call*****</b>\n{format_tool_calls(obj1['tool_calls'])}\n"
        elif obj1.get("tool_responses") and len(obj1["tool_responses"]) > 0:
            return f"<b>{obj['from']} -> {obj['to']}:</b> <b>*****Tool Response*****</b>\n{obj1['content']}\n"
        elif obj1.get("content"):
            return f"<b>{obj['from']} -> {obj['to']}:</b>\n{obj1['content']}"
        else:
            raise Exception("Unknown message type")
    else:
        raise Exception("Unknown message type")

def format_tool_calls(tool_calls: List[Dict[str, Any]]) -> str:
    return "\n".join([
        f"{x['function']['name']}\n{json.dumps(json.loads(x['function']['arguments']), indent=2)}\n"
        for x in tool_calls
    ])