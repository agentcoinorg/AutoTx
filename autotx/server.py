import asyncio
from datetime import datetime
from typing import Any, Dict, List, cast
import uuid
from fastapi import APIRouter, FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config

from autotx import models, setup

from autotx import models
from autotx.AutoTx import AutoTx
from autotx.AutoTx import Config as AutoTxConfig
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.configuration import get_configuration
from autotx.utils.ethereum import SafeManager, load_w3
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.wallets.api_smart_wallet import ApiSmartWallet
from autotx.wallets.smart_wallet import SmartWallet

class AutoTxParams:
    verbose: bool
    logs: str | None
    cache: bool
    max_rounds: int | None
    is_dev: bool
    dev_wallet: SmartWallet | None

    def __init__(self, 
        verbose: bool, 
        logs: str | None, 
        cache: bool,
        max_rounds: int | None, 
        is_dev: bool,
        dev_wallet: SmartWallet | None,
    ):
        self.verbose = verbose
        self.logs = logs
        self.cache = cache
        self.max_rounds = max_rounds
        self.is_dev = is_dev
        self.dev_wallet = dev_wallet

tasks: list[models.Task] = []

autotx_params: AutoTxParams | None = None

app_router = APIRouter()

@app_router.post("/api/v1/tasks", response_model=models.Task)
async def create_task(task: models.TaskCreate, background_tasks: BackgroundTasks) -> 'models.Task':
    global tasks
    global autotx_params
    if autotx_params is None:
        raise HTTPException(status_code=500, detail="AutoTx not started")

    if not autotx_params.is_dev and not task.address:
        raise HTTPException(status_code=400, detail="Address is required for non-dev mode")
    
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    created_task = models.Task(
        id=task_id,
        prompt=task.prompt,
        created_at=now,
        updated_at=now,
        running=True,
        messages=[],
        transactions=[],
    )
    tasks.append(created_task)
    prompt = task.prompt

    print(f"Starting task: {task_id}")

    (get_llm_config, agents, logs_dir) = setup.setup_agents(autotx_params.logs, cache=autotx_params.cache)

    web3 = load_w3()
    chain_id = web3.eth.chain_id
    network_info = NetworkInfo(chain_id)    

    wallet: SmartWallet
    if autotx_params.is_dev:
        wallet = cast(SmartWallet, autotx_params.dev_wallet)
    else:
        wallet = ApiSmartWallet(ETHAddress(cast(str, task.address)), task_id, tasks)

    autotx = AutoTx(
        wallet,
        network_info,
        agents,
        AutoTxConfig(verbose=autotx_params.verbose, get_llm_config=get_llm_config, logs_dir=logs_dir, max_rounds=autotx_params.max_rounds),
    )

    async def run_task() -> None:
        await autotx.a_run(prompt, non_interactive=True)
        saved_task = next(filter(lambda x: x.id == task_id, tasks), None)
        if saved_task is None:
            raise Exception("Task not found: " + task_id)

        saved_task.running = False
        saved_task.messages = autotx.info_messages

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

    dev_wallet: SmartWallet | None = None

    if is_dev: 
        (smart_account_addr, agent, client) = get_configuration()
        (wallet, _network, _web3) = setup.setup_safe(smart_account_addr, agent, client, interactive=False)
        dev_wallet = wallet

    global autotx_params
    autotx_params = AutoTxParams(
        verbose=verbose, 
        logs=logs,
        cache=cache,
        max_rounds=max_rounds, 
        is_dev=is_dev,
        dev_wallet=dev_wallet,
    )

def start_server(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool, port: int | None, is_dev: bool) -> None:
    setup_server(verbose, logs, max_rounds, cache, is_dev)

    port = port or 8000
    config = Config()
    config.bind = [f"localhost:{port}"]
    asyncio.run(serve(app, config)) # type: ignore
