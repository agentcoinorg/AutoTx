from datetime import datetime
import json
import os
import uuid
from pydantic import BaseModel
from supabase import create_client
from supabase.client import Client
from supabase.lib.client_options import ClientOptions

from autotx import models

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise Exception("No supabase url provided")

if not SUPABASE_KEY:
    raise Exception("No supabase service role key provided")

def get_db_client(schema: str) -> Client:
    if not SUPABASE_URL:
        raise Exception("No supabase url provided")

    if not SUPABASE_KEY:
        raise Exception("No supabase service role key provided")

    options = ClientOptions(schema=schema)
    return create_client(SUPABASE_URL, SUPABASE_KEY, options)

class TasksRepository:
    def __init__(self, app_id: str):
        self.client = get_db_client("public")
        self.app_id = app_id

    def start(self, prompt: str, address: str, chain_id: int, app_user_id: str) -> models.Task:
        client = get_db_client("public")

        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()

        result = client.table("tasks").insert(
            {
                "app_id": self.app_id,
                "app_user_id": app_user_id,
                "prompt": prompt,
                "address": address,
                "chain_id": chain_id,
                "running": True,
                "error": None,
                "created_at": str(created_at),
                "updated_at": str(updated_at),
                "messages": json.dumps([]),
                "transactions": json.dumps([])
            }
        ).execute()

        return models.Task(
            id=result.data[0]["id"],
            prompt=prompt,
            address=address,
            chain_id=chain_id,
            created_at=created_at,
            updated_at=updated_at,
            running=True,
            error=None,
            messages=[],
            transactions=[]
        )

    def stop(self, task_id: str) -> None:
        client = get_db_client("public")

        client.table("tasks").update(
            {
                "running": False,
                "updated_at": str(datetime.utcnow())
            }
        ).eq("id", task_id).eq("app_id", self.app_id).execute()

    def update(self, task: models.Task) -> None:
        client = get_db_client("public")

        txs = [json.loads(tx.json()) for tx in task.transactions]

        client.table("tasks").update(
            {
                "prompt": task.prompt,
                "running": task.running,
                "updated_at": str(datetime.utcnow()),
                "messages": json.dumps(task.messages),
                "error": task.error,
                "transactions": json.dumps(txs)
            }
        ).eq("id", task.id).eq("app_id", self.app_id).execute()

    def get(self, task_id: str) -> models.Task | None:
        client = get_db_client("public")

        result = client.table("tasks") \
            .select("*") \
            .eq("id", task_id) \
            .eq("app_id", self.app_id) \
            .execute()

        if len(result.data) == 0:
            return None

        task_data = result.data[0]

        return models.Task(
            id=task_data["id"],
            prompt=task_data["prompt"],
            address=task_data["address"],
            chain_id=task_data["chain_id"],
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"],
            running=task_data["running"],
            error=task_data["error"],
            messages=json.loads(task_data["messages"]),
            transactions=json.loads(task_data["transactions"])
        )

    def get_all(self) -> list[models.Task]:
        client = get_db_client("public")

        result = client.table("tasks").select("*").eq("app_id", self.app_id).execute()

        tasks = []

        for task_data in result.data:
            tasks.append(
                models.Task(
                    id=task_data["id"],
                    prompt=task_data["prompt"],
                    address=task_data["address"],
                    chain_id=task_data["chain_id"],
                    created_at=task_data["created_at"],
                    updated_at=task_data["updated_at"],
                    running=task_data["running"],
                    error=task_data["error"],
                    messages=json.loads(task_data["messages"]),
                    transactions=json.loads(task_data["transactions"])
                )
            )

        return tasks
    
def get_app_by_api_key(api_key: str) -> models.App | None:
    client = get_db_client("public")

    result = client.table("apps").select("*").eq("api_key", api_key).execute()

    if len(result.data) == 0:
        return None

    app_data = result.data[0]

    return models.App(
        id=app_data["id"],
        name=app_data["name"],
        api_key=app_data["api_key"],
        allowed=app_data["allowed"]
    )


def create_app_user(app_id: str, user_id: str, agent_address: str, agent_private_key: str) -> models.AppUser: 
    client = get_db_client("public")
    
    created_at = datetime.utcnow()
    result = client.table("app_users").insert(
        {
            "app_id": app_id,
            "created_at": str(created_at),
            "user_id": user_id,
            "agent_address": agent_address,
            "agent_private_key": agent_private_key
        }
    ).execute()

    return models.AppUser(
        id=result.data[0]["id"],
        user_id=user_id,
        agent_address=agent_address,
        created_at=created_at,
        app_id=app_id
    )

def get_app_user(app_id: str, user_id: str) -> models.AppUser | None:
    client = get_db_client("public")

    result = client.table("app_users") \
        .select("*") \
        .eq("app_id", app_id) \
        .eq("user_id", user_id) \
        .execute()

    if len(result.data) == 0:
        return None

    app_user_data = result.data[0]

    return models.AppUser(
        id = app_user_data["id"],
        user_id=app_user_data["user_id"],
        agent_address=app_user_data["agent_address"],
        created_at=app_user_data["created_at"],
        app_id=app_user_data["app_id"]
    )

def get_agent_private_key(app_id: str, user_id: str) -> str | None:
    client = get_db_client("public")

    result = client.table("app_users") \
        .select("agent_private_key") \
        .eq("app_id", app_id) \
        .eq("user_id", user_id) \
        .execute()

    if len(result.data) == 0:
        return None

    return str(result.data[0]["agent_private_key"])

def submit_transactions(app_id: str, address: str, chain_id: int, app_user_id: str, task_id: str) -> None:
    client = get_db_client("public")
    
    created_at = datetime.utcnow()
    client.table("submitted_batches") \
        .insert(
            {
                "app_id": app_id,
                "address": address,
                "chain_id": chain_id,
                "app_user_id": app_user_id,
                "task_id": task_id,
                "created_at": str(created_at)
            }
        ).execute()
    
class SubmittedBatch(BaseModel):
    id: str
    app_id: str
    address: str
    chain_id: int
    app_user_id: str
    task_id: str
    created_at: datetime

def get_submitted_batches(app_id: str, task_id: str) -> list[SubmittedBatch]:
    client = get_db_client("public")

    result = client.table("submitted_batches") \
        .select("*") \
        .eq("app_id", app_id) \
        .eq("task_id", task_id) \
        .execute()
    
    batches = []

    for batch_data in result.data:
        batches.append(
            SubmittedBatch(
                id=batch_data["id"],
                app_id=batch_data["app_id"],
                address=batch_data["address"],
                chain_id=batch_data["chain_id"],
                app_user_id=batch_data["app_user_id"],
                task_id=batch_data["task_id"],
                created_at=batch_data["created_at"]
            )
        )

    return batches

def create_app(name: str, api_key: str) -> models.App:
    client = get_db_client("public")

    result = client.table("apps").insert(
        {
            "name": name,
            "api_key": api_key,
            "allowed": True
        }
    ).execute()

    return models.App(
        id=result.data[0]["id"],
        name=name,
        api_key=api_key,
        allowed=True
    )

def clear_db() -> None:
    client = get_db_client("public")

    uid = uuid.uuid4().hex

    client.table("apps").delete().neq("id", uid).execute()
    client.table("app_users").delete().neq("id", uid).execute()
    client.table("tasks").delete().neq("id", uid).execute()
    client.table("submitted_batches").delete().neq("id", uid).execute()