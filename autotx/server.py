from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List
import uuid
from fastapi import APIRouter, FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from autotx import models, setup
from autotx.AutoTx import AutoTx, Config as AutoTxConfig
from autotx.utils.configuration import AppConfig
from autotx.utils.ethereum.chain_short_names import CHAIN_ID_TO_SHORT_NAME
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_CONFIGURATION_MAP
from autotx.wallets.api_smart_wallet import ApiSmartWallet
from autotx.wallets.smart_wallet import SmartWallet

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
        max_rounds: int | None, 
        is_dev: bool,
    ):
        self.verbose = verbose
        self.logs = logs
        self.cache = cache
        self.max_rounds = max_rounds
        self.is_dev = is_dev

tasks: list[models.Task] = []

autotx_params: AutoTxParams | None = None

app_router = APIRouter()

@app_router.post("/api/v1/tasks", response_model=models.Task)
async def create_task(task: models.TaskCreate, background_tasks: BackgroundTasks) -> 'models.Task':
    global tasks
    global autotx_params
    if autotx_params is None:
        raise HTTPException(status_code=500, detail="AutoTx not started")

    if not autotx_params.is_dev and (not task.address or not task.chain_id):
        raise HTTPException(status_code=400, detail="Address and Chain ID are required for non-dev mode")
    
    task_id = str(uuid.uuid4())
    prompt = task.prompt
    
    app_config = AppConfig.load(smart_account_addr=task.address, subsidized_chain_id=task.chain_id)

    wallet: SmartWallet
    if autotx_params.is_dev:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, task_id, tasks)
    else:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, task_id, tasks)

    now = datetime.utcnow()
    created_task = models.Task(
        id=task_id,
        prompt=prompt,
        address=wallet.address.hex,
        chain_id=app_config.network_info.chain_id,
        created_at=now,
        updated_at=now,
        running=True,
        messages=[],
        transactions=[],
    )
    tasks.append(created_task)
    
    (get_llm_config, agents, logs_dir) = setup.setup_agents(autotx_params.logs, cache=autotx_params.cache)

    def on_notify_user(message: str) -> None:
        created_task.messages.append(message)
        created_task.updated_at = datetime.utcnow()

    autotx = AutoTx(
        app_config.web3,
        wallet,
        app_config.network_info,
        agents,
        AutoTxConfig(verbose=autotx_params.verbose, get_llm_config=get_llm_config, logs_dir=logs_dir, max_rounds=autotx_params.max_rounds),
        on_notify_user=on_notify_user
    )

    async def run_task() -> None:
        await autotx.a_run(prompt, non_interactive=True)
        saved_task = next(filter(lambda x: x.id == task_id, tasks), None)
        if saved_task is None:
            raise Exception("Task not found: " + task_id)

        saved_task.running = False
        saved_task.updated_at = datetime.utcnow()

    background_tasks.add_task(run_task)

    return created_task

@app_router.get("/api/v1/tasks", response_model=List[models.Task])
def get_tasks() -> List['models.Task']:
    global tasks
    return tasks

@app_router.get("/api/v1/tasks/{task_id}", response_model=models.Task)
def get_task(task_id: str) -> 'models.Task':
    global tasks
    task = next(filter(lambda x: x.id == task_id, tasks), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app_router.get("/api/v1/tasks/{task_id}/transactions", response_model=List[models.Transaction])
def get_transactions(task_id: str) -> Any:
    global tasks
    task = next(filter(lambda x: x.id == task_id, tasks), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.transactions

class SendTransactionsParams(BaseModel):
    address: str
    chain_id: int

@app_router.post("/api/v1/tasks/{task_id}/transactions")
def send_transactions(task_id: str, model: SendTransactionsParams) -> str:
    global tasks
    task = next(filter(lambda x: x.id == task_id, tasks), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.running:
        raise HTTPException(status_code=400, detail="Task is still running")
    
    app_config = AppConfig.load(smart_account_addr=task.address, subsidized_chain_id=task.chain_id)

    app_config.manager.send_tx_batch(
        task.transactions,
        require_approval=False,
    )

    return f"https://app.safe.global/transactions/queue?safe={CHAIN_ID_TO_SHORT_NAME[str(model.chain_id)]}:{model.address}"

class SupportedNetwork(BaseModel):
    name: str
    chain_id: int

@app_router.get("/api/v1/supported-networks", response_model=List[SupportedNetwork])
def get_supported_networks() -> list[SupportedNetwork]:
    return [
        SupportedNetwork(name=config.network_name, chain_id=chain_id)
        for chain_id, config in SUPPORTED_NETWORKS_CONFIGURATION_MAP.items()
    ]

class FeedbackParams(BaseModel):
    feedback: str

@app_router.post("/api/v1/tasks/{task_id}/feedback", response_model=models.Task)
def provide_feedback(task_id: str, model: FeedbackParams, background_tasks: BackgroundTasks) -> 'models.Task':
    global tasks
    task = next(filter(lambda x: x.id == task_id, tasks), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.running:
        raise HTTPException(status_code=400, detail="Task is still running")
        
    global autotx_params
    if autotx_params is None:
        raise HTTPException(status_code=500, detail="AutoTx not started")

    if not autotx_params.is_dev and (not task.address or not task.chain_id):
        raise HTTPException(status_code=400, detail="Address and Chain ID are required for non-dev mode")
    
    app_config = AppConfig.load(smart_account_addr=task.address, subsidized_chain_id=task.chain_id)

    (get_llm_config, agents, logs_dir) = setup.setup_agents(autotx_params.logs, cache=autotx_params.cache)

    wallet: SmartWallet
    if autotx_params.is_dev:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, task_id, tasks)
    else:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, task_id, tasks)

    def on_notify_user(message: str) -> None:
        task.messages.append(message)
        task.updated_at = datetime.utcnow()

    autotx = AutoTx(
        app_config.web3,
        wallet,
        app_config.network_info,
        agents,
        AutoTxConfig(verbose=autotx_params.verbose, get_llm_config=get_llm_config, logs_dir=logs_dir, max_rounds=autotx_params.max_rounds),
        on_notify_user=on_notify_user
    )

    transactions_info = "\n".join(
        [
            f"{i + 1}. {tx.summary}"
            for i, tx in enumerate(task.transactions)
        ]
    )

    prev_history = dedent(f"""
        Then you prepared these transactions to accomplish the goal:
        {transactions_info}
        Then the user provided feedback:
        {model.feedback}"""
    )

    task.prompt = (f"\nOriginaly the user said: {task.prompt}"
        + prev_history
        + "\nPay close attention to the user's feedback and try again.")
    task.transactions = []
    task.running = True
    task.updated_at = datetime.utcnow()
    task.messages = []

    prompt = task.prompt

    async def run_task() -> None:
            await autotx.a_run(prompt, non_interactive=True)
            saved_task = next(filter(lambda x: x.id == task_id, tasks), None)
            if saved_task is None:
                raise Exception("Task not found: " + task_id)

            saved_task.running = False
            saved_task.messages = autotx.info_messages
            saved_task.updated_at = datetime.utcnow()

    background_tasks.add_task(run_task)

    return task

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

def setup_server(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool, is_dev: bool) -> None:
    global tasks
    tasks = []

    if is_dev: 
        AppConfig.load() # Loading the configuration deploys the dev wallet in dev mode

    global autotx_params
    autotx_params = AutoTxParams(
        verbose=verbose, 
        logs=logs,
        cache=cache,
        max_rounds=max_rounds, 
        is_dev=is_dev,
    )