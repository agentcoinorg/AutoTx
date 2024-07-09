from datetime import datetime
import json
from typing import Annotated, Any, Dict, List
from eth_account import Account
from eth_account.signers.local import LocalAccount
from gnosis.safe.api.base_api import SafeAPIException
from fastapi import APIRouter, FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import traceback

from autotx import models, setup, task_logs
from autotx import db
from autotx.AutoTx import AutoTx, Config as AutoTxConfig
from autotx.intents import Intent
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.transactions import Transaction
from autotx.utils.configuration import AppConfig
from autotx.utils.ethereum.chain_short_names import CHAIN_ID_TO_SHORT_NAME
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_CONFIGURATION_MAP
from autotx.smart_accounts.api_smart_account import ApiSmartAccount
from autotx.smart_accounts.safe_smart_account import SafeSmartAccount

class AutoTxParams:
    verbose: bool
    logs: str | None
    cache: bool
    max_rounds: int | None
    is_dev: bool

    def __init__(self, 
        verbose: bool, 
        logs: str | None, 
        cache: bool,
        is_dev: bool,
        max_rounds: int | None = None
    ):
        self.verbose = verbose
        self.logs = logs
        self.cache = cache
        self.max_rounds = max_rounds
        self.is_dev = is_dev

autotx_params: AutoTxParams = AutoTxParams(verbose=False, logs=None, cache=False, is_dev=False)

app_router = APIRouter()

def get_task_or_404(task_id: str, tasks: db.TasksRepository) -> models.Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

def authorize(authorization: str | None) -> models.App:
    if not authorization or authorization.startswith("Bearer ") is False:
        raise HTTPException(status_code=401, detail="Unauthorized")

    api_key = authorization.split("Bearer ")[1]
    app = db.get_app_by_api_key(api_key)

    if not app or app.allowed is False:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return app

def load_wallet_for_user(app_config: AppConfig, app_id: str, user_id: str, address: str) -> SmartAccount:
    agent_private_key = db.get_agent_private_key(app_id, user_id)

    if not agent_private_key:
        raise HTTPException(status_code=400, detail="User not found")

    agent = Account.from_key(agent_private_key)

    wallet = SafeSmartAccount(app_config.rpc_url, app_config.network_info, auto_submit_tx=False, smart_account_addr=address, agent=agent)

    return wallet

def authorize_app_and_user(authorization: str | None, user_id: str) -> tuple[models.App, models.AppUser]:
    app = authorize(authorization)
    app_user = db.get_app_user(app.id, user_id)

    if not app_user:
        raise HTTPException(status_code=400, detail="User not found")

    return (app, app_user)

async def build_transactions(app_id: str, user_id: str, chain_id: int, address: str, task: models.Task) -> List[Transaction]:
    if task.running:
        raise HTTPException(status_code=400, detail="Task is still running")

    app_config = AppConfig(subsidized_chain_id=chain_id)
    wallet = load_wallet_for_user(app_config, app_id, user_id, address)

    if task.intents is None or len(task.intents) == 0:
        return []

    transactions: list[Transaction] = []

    for intent in task.intents:
        transactions.extend(await intent.build_transactions(app_config.web3, app_config.network_info, wallet.address))

    return transactions

def stop_task_for_error(tasks: db.TasksRepository, task_id: str, error: str, user_error_message: str) -> None:
    task = tasks.get(task_id)
    if task is None:
        raise Exception("Task not found: " + task_id)

    task.error = error
    task.running = False
    task.messages.append(user_error_message)
    tasks.update(task)

def log(log_type: str, obj: Any, task_id: str, tasks: db.TasksRepository) -> None:
   add_task_log(models.TaskLog(type=log_type, obj=json.dumps(obj), created_at=datetime.now()), task_id, tasks)

def add_task_log(log: models.TaskLog, task_id: str, tasks: db.TasksRepository) -> None:
    task = tasks.get(task_id)
    if task is None:
        raise Exception("Task not found: " + task_id)

    if task.logs is None:
        task.logs = []
    task.logs.append(log)
    tasks.update(task)


def get_previous_tasks(task: models.Task, tasks: db.TasksRepository) -> List[models.Task]:
    previous_tasks = []
    current_task: models.Task | None = task
    while current_task is not None:
        previous_tasks.append(current_task)
        if current_task.previous_task_id is None:
            break
        current_task = tasks.get(current_task.previous_task_id)
    return previous_tasks

def run_task(prompt: str, task: models.TaskCreate, app: models.App, app_user: models.AppUser, tasks: db.TasksRepository, background_tasks: BackgroundTasks, previous_task_id: str | None = None) -> models.Task:
    app_config = AppConfig(subsidized_chain_id=task.chain_id)

    wallet = SafeSmartAccount(app_config.rpc_url, app_config.network_info, smart_account_addr=task.address)
    api_wallet = ApiSmartAccount(app_config.web3, wallet, tasks)

    created_task: models.Task = tasks.start(prompt, api_wallet.address.hex, app_config.network_info.chain_id.value, app_user.id, previous_task_id)
    task_id = created_task.id
    api_wallet.task_id = task_id

    try:
        (get_llm_config, agents, logs_dir) = setup.setup_agents(autotx_params.logs, cache=autotx_params.cache)

        def on_notify_user(message: str) -> None:
            task = tasks.get(task_id)
            if task is None:
                raise Exception("Task not found: " + task_id)

            task.messages.append(message)
            tasks.update(task)

        def on_agent_message(from_agent: str, to_agent: str, message: Any) -> None:
            add_task_log(
                task_logs.build_agent_message_log(from_agent, to_agent, message),
                task_id,
                tasks
            )

        autotx = AutoTx(
            app_config.web3,
            api_wallet,
            app_config.network_info,
            agents,
            AutoTxConfig(
                verbose=autotx_params.verbose, 
                get_llm_config=get_llm_config, 
                logs_dir=logs_dir, 
                max_rounds=autotx_params.max_rounds,
                on_agent_message=on_agent_message,
            ),
            on_notify_user=on_notify_user,
        )

        async def run_task() -> None:
            try: 
                log("execution", "run-start", task_id, tasks)
                await autotx.a_run(prompt, non_interactive=True)
                log("execution", "run-end", task_id, tasks)
            except Exception as e:
                error = traceback.format_exc()
                db.add_task_error(f"AutoTx run", app.id, app_user.id, task_id, error)
                stop_task_for_error(tasks, task_id, error, f"An error caused AutoTx to stop ({task_id})")
                raise e
            tasks.stop(task_id)
            log("execution", "task-stop", task_id, tasks)

        background_tasks.add_task(run_task)

        return created_task
    except Exception as e:
        error = traceback.format_exc()
        db.add_task_error(f"Route: create_task", app.id, app_user.id, task_id, error)
        stop_task_for_error(tasks, task_id, error, f"An error caused AutoTx to stop ({task_id})")
        raise e

@app_router.post("/api/v1/tasks", response_model=models.Task)
async def create_task(task: models.TaskCreate, background_tasks: BackgroundTasks, authorization: Annotated[str | None, Header()] = None) -> models.Task:   
    app = authorize(authorization)
    app_user = db.get_app_user(app.id, task.user_id)
    if not app_user:
        raise HTTPException(status_code=400, detail="User not found")

    tasks = db.TasksRepository(app.id)

    global autotx_params
    if not autotx_params.is_dev and (not task.address or not task.chain_id):
        raise HTTPException(status_code=400, detail="Address and Chain ID are required for non-dev mode")
    
    prompt = task.prompt
    
    created_task = run_task(prompt, task, app, app_user, tasks, background_tasks)

    return created_task

class FeedbackParams(BaseModel):
    feedback: str
    user_id: str

@app_router.post("/api/v1/tasks/{task_id}/feedback", response_model=models.Task)
def provide_feedback(task_id: str, model: FeedbackParams, background_tasks: BackgroundTasks, authorization: Annotated[str | None, Header()] = None) -> 'models.Task':
    (app, app_user) = authorize_app_and_user(authorization, model.user_id)

    tasks = db.TasksRepository(app.id)
    
    task = get_task_or_404(task_id, tasks)

    if task.running:
        raise HTTPException(status_code=400, detail="Task is still running")
    
    global autotx_params
    if not autotx_params.is_dev and (not task.address or not task.chain_id):
        raise HTTPException(status_code=400, detail="Address and Chain ID are required for non-dev mode")
    
    # Get all previous tasks
    previous_tasks = get_previous_tasks(task, tasks)

    prompt = "History:\n"
    for previous_task in previous_tasks[::-1]:
        if previous_task.previous_task_id is None:
            prompt += "The user first said:\n"+ previous_task.prompt + "\n\n"
        prompt += "Then the agents generated the following transactions:\n"
        for intent in previous_task.intents:
            prompt += intent.summary + "\n"
        prompt += "\n"
        if previous_task.feedback:
            prompt += "The user then said:\n" + previous_task.feedback + "\n\n"

    prompt += "Now the user provided feedback:\n" + model.feedback
    
    tasks.update_feedback(task_id, model.feedback)

    created_task = run_task(prompt, models.TaskCreate(prompt=prompt, address=task.address, chain_id=task.chain_id, user_id=app_user.user_id), app, app_user, tasks, background_tasks, task_id)

    return created_task

@app_router.post("/api/v1/connect", response_model=models.AppUser)
async def connect(model: models.ConnectionCreate, authorization: Annotated[str | None, Header()] = None) -> models.AppUser:
    app = authorize(authorization)

    app_user = db.get_app_user(app.id, model.user_id)

    if app_user:
        return app_user
    else:
        agent_acc: LocalAccount = Account.create()
        agent_private_key: str = agent_acc.key.hex()
        agent_address: str = agent_acc.address

        app_user = db.create_app_user(app.id, model.user_id, agent_address, agent_private_key)

        return app_user

@app_router.get("/api/v1/tasks", response_model=List[models.Task])
def get_tasks(authorization: Annotated[str | None, Header()] = None) -> List['models.Task']:
    app = authorize(authorization)
    tasks = db.TasksRepository(app.id)
   
    all_tasks: list[models.Task] = tasks.get_all()
    return all_tasks

@app_router.get("/api/v1/tasks/{task_id}", response_model=models.Task)
def get_task(task_id: str, authorization: Annotated[str | None, Header()] = None) -> 'models.Task':
    app = authorize(authorization)
    tasks = db.TasksRepository(app.id)

    task = get_task_or_404(task_id, tasks)
    return task

@app_router.get("/api/v1/tasks/user/{user_id}")
def get_user_tasks(
    user_id: str, authorization: Annotated[str | None, Header()] = None
) -> str:
    (_, app_user) = authorize_app_and_user(authorization, user_id)
    return [
        {**task, "transactions": db.get_transactions_from_task(task.id)}
        for task in db.TasksRepository().get_all()
        if task.app_user_id == app_user.id
    ]

@app_router.get("/api/v1/tasks/{task_id}/intents", response_model=List[Intent])
def get_intents(task_id: str, authorization: Annotated[str | None, Header()] = None) -> Any:
    app = authorize(authorization)
    tasks = db.TasksRepository(app.id)
    
    task = get_task_or_404(task_id, tasks)
    return task.intents

@app_router.get("/api/v1/tasks/{task_id}/transactions", response_model=List[Transaction])
async def get_transactions(
    task_id: str, 
    address: str,
    chain_id: int,
    user_id: str, 
    authorization: Annotated[str | None, Header()] = None
) -> List[Transaction]:
    (app, app_user) = authorize_app_and_user(authorization, user_id)

    tasks = db.TasksRepository(app.id)
    
    task = get_task_or_404(task_id, tasks)

    try:
        if task.chain_id != chain_id:
            raise HTTPException(status_code=400, detail="Chain ID does not match task")

        transactions = await build_transactions(app.id, user_id, chain_id, address, task)
    except Exception as e:
        db.add_task_error(f"Route: get_transactions", app.id, app_user.id, task_id, traceback.format_exc())
        raise e

    return transactions

class PreparedTransactionsDto(BaseModel):
    batch_id: str
    transactions: List[Transaction]

@app_router.post("/api/v1/tasks/{task_id}/transactions/prepare", response_model=PreparedTransactionsDto)
async def prepare_transactions(
    task_id: str, 
    address: str,
    chain_id: int,
    user_id: str, 
    authorization: Annotated[str | None, Header()] = None
) -> PreparedTransactionsDto:
    (app, app_user) = authorize_app_and_user(authorization, user_id)

    tasks = db.TasksRepository(app.id)
    
    task = get_task_or_404(task_id, tasks)

    try:
        if task.chain_id != chain_id:
            raise HTTPException(status_code=400, detail="Chain ID does not match task")
        
        transactions = await build_transactions(app.id, app_user.user_id, chain_id, address, task)

        if len(transactions) == 0:
            raise HTTPException(status_code=400, detail="No transactions to send")

        submitted_batch_id = db.save_transactions(app.id, address, chain_id, app_user.id, task_id, transactions)
    except Exception as e:
        db.add_task_error(f"Route: prepare_transactions", app.id, app_user.id, task_id, traceback.format_exc())
        raise e

    return PreparedTransactionsDto(batch_id=submitted_batch_id, transactions=transactions)

@app_router.post("/api/v1/tasks/{task_id}/transactions")
async def send_transactions(
    task_id: str, 
    address: str,
    chain_id: int,
    user_id: str, 
    batch_id: str,
    authorization: Annotated[str | None, Header()] = None
) -> str:
    (app, app_user) = authorize_app_and_user(authorization, user_id)

    tasks = db.TasksRepository(app.id)
    
    task = get_task_or_404(task_id, tasks)

    if task.chain_id != chain_id:
        raise HTTPException(status_code=400, detail="Chain ID does not match task")

    try:
        batch = db.get_transactions(app.id, app_user.id, task_id, address, chain_id, batch_id)

        if batch is None:
            raise HTTPException(status_code=400, detail="Batch not found")

        (transactions, task_id) = batch

        if len(transactions) == 0:
            raise HTTPException(status_code=400, detail="No transactions to send")

        global autotx_params
        if autotx_params.is_dev:
            print("Dev mode: skipping transaction submission")
            db.submit_transactions(app.id, app_user.id, batch_id)
            return f"https://app.safe.global/transactions/queue?safe={CHAIN_ID_TO_SHORT_NAME[str(chain_id)]}:{address}"

        try:
            app_config = AppConfig(subsidized_chain_id=chain_id)
            wallet = load_wallet_for_user(app_config, app.id, user_id, address)

            await wallet.send_transactions(transactions)
        except SafeAPIException as e:
            if "is not an owner or delegate" in str(e):
                raise HTTPException(status_code=400, detail="Agent is not an owner or delegate")
            else:
                raise e
            
        db.submit_transactions(app.id, app_user.id, batch_id)
    except Exception as e:
        db.add_task_error(f"Route: send_transactions", app.id, app_user.id, task_id, traceback.format_exc())
        raise e
        
    db.submit_transactions(app.id, app_user.id, batch_id)

    return f"https://app.safe.global/transactions/queue?safe={CHAIN_ID_TO_SHORT_NAME[str(chain_id)]}:{address}"

@app_router.get("/api/v1/networks", response_model=List[models.SupportedNetwork])
def get_supported_networks() -> list[models.SupportedNetwork]:
    return [
        models.SupportedNetwork(name=config.network_name, chain_id=chain_id)
        for chain_id, config in SUPPORTED_NETWORKS_CONFIGURATION_MAP.items()
    ]

@app_router.get("/api/v1/tasks/{task_id}/logs", response_model=list[models.TaskLog])
def get_task_logs(task_id: str) -> list[models.TaskLog]:
    logs = db.get_task_logs(task_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return logs

@app_router.get("/api/v1/tasks/{task_id}/logs/{log_type}", response_class=HTMLResponse)
def get_task_logs_formatted(task_id: str, log_type: str) -> str:
    if log_type != "agent-message" and log_type != "execution":
        raise HTTPException(status_code=400, detail="Log type not supported")
    
    logs = db.get_task_logs(task_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Task not found")

    filtered_logs = [log for log in logs if log.type == log_type]

    if len(filtered_logs) == 0:
        return "<pre>No logs found</pre>"
    
    if log_type == "execution":
        return "<pre>" + "\n".join([log.created_at.strftime("%Y-%m-%d %H:%M:%S") + f": {json.loads(log.obj)}" for log in filtered_logs]) + "</pre>"
    else:
        agent_logs = [task_logs.format_agent_message_log(json.loads(log.obj)) for log in filtered_logs]

        text = "\n\n".join(agent_logs)
        return f"<pre>{text}</pre>"

@app_router.get("/api/v1/version", response_class=JSONResponse)
async def get_version() -> Dict[str, str]:
    return {"version": "0.1.0"}

app = FastAPI()

app.include_router(app_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_server(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool, is_dev: bool, check_valid_safe: bool) -> None:
    if is_dev: 
        app_config = AppConfig() 
        # Loading the SafeSmartAccount will deploy a new Safe if one is not already deployed
        SafeSmartAccount(app_config.rpc_url, app_config.network_info, fill_dev_account=True, check_valid_safe=check_valid_safe)

    global autotx_params
    autotx_params = AutoTxParams(
        verbose=verbose, 
        logs=logs,
        cache=cache,
        max_rounds=max_rounds, 
        is_dev=is_dev,
    )