from fastapi import HTTPException
from flask import Request
from flask.typing import ResponseReturnValue
import functions_framework
from autotx import db
from autotx.server import authorize_app_and_user


@functions_framework.http
def get_user_tasks(request: Request) -> ResponseReturnValue:
    if request.method != "GET":
        return "Method not allowed"

    try:
        (app, app_user) = authorize_app_and_user(
            request.authorization, request.args["userDid"]
        )
        tasks = db.TasksRepository(app_id=app.id).get_from_user(app_user.id)
        user_tasks = [
            {
                "id": task.id,
                "prompt": task.prompt,
                "address": task.address,
                "chain_id": task.chain_id,
                "intents": task.intents,
            }
            for task in tasks
        ]
        user_submitted_transactions = [
            batch
            for batch in db.get_submitted_transactions_from_user(app.id, app_user.id)
        ]

        return {
            "tasks": user_tasks,
            "submitted_transactions": user_submitted_transactions,
        }
    except HTTPException as e:
        return {"status": e.status_code, "message": e.detail}
    except Exception as e:
        print(e)
        return {"status": 500, "message": "Internal error"}
