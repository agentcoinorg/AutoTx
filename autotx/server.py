import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
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
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo

class AutoTxParams:
    verbose: bool
    logs_dir: str | None
    max_rounds: int | None
    manager: SafeManager
    network_info: NetworkInfo
    agents: list[AutoTxAgent]
    get_llm_config: Callable[[], Optional[Dict[str, Any]]]

    def __init__(self, 
        verbose: bool, 
        logs_dir: str | None, 
        max_rounds: int | None, 
        manager: SafeManager, 
        network_info: NetworkInfo, 
        agents: list[AutoTxAgent], 
        get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    ):
        self.verbose = verbose
        self.logs_dir = logs_dir
        self.max_rounds = max_rounds
        self.manager = manager
        self.network_info = network_info
        self.agents = agents
        self.get_llm_config = get_llm_config

tasks: list[models.Task] = []

autotx_params: AutoTxParams | None = None

app_router = APIRouter()

@app_router.post("/api/v1/tasks", response_model=models.Task)
async def create_task(task: models.TaskCreate, background_tasks: BackgroundTasks) -> 'models.Task':
    global tasks
    global autotx_params
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

    print(f"Starting task: {task_id}")

    prompt = task.prompt

    if autotx_params is None:
        raise HTTPException(status_code=500, detail="AutoTx not started")

    def on_transactions_added(txs: List[models.Transaction]) -> None:
        saved_task = next(filter(lambda x: x.id == task_id, tasks), None)
        if saved_task is None:
            raise Exception("Task not found: " + task_id)
        for tx in txs:
            tx.id = str(uuid.uuid4())
            tx.task_id = task_id

        saved_task.transactions.extend(txs)

    autotx = AutoTx(
        autotx_params.manager,
        autotx_params.network_info,
        autotx_params.agents,
        AutoTxConfig(verbose=autotx_params.verbose, logs_dir=autotx_params.logs_dir, max_rounds=autotx_params.max_rounds),
        get_llm_config=autotx_params.get_llm_config,
        on_transactions_added=on_transactions_added,
    )

    async def run_task() -> None:
        await autotx.run(prompt, non_interactive=True)
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

def setup_server(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool | None) -> None:
    global tasks
    tasks = []

    (smart_account_addr, agent, client) = get_configuration()

    (manager, network_info, _web3) = setup.setup_safe(smart_account_addr, agent, client)

    (get_llm_config, agents, logs_dir) = setup.setup_agents(manager, logs, cache=cache)

    global autotx_params
    autotx_params = AutoTxParams(
        verbose=verbose, 
        logs_dir=logs_dir, 
        max_rounds=max_rounds, 
        manager=manager, 
        network_info=network_info, 
        agents=agents, 
        get_llm_config=get_llm_config
    )

def start_server(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool | None, port: int | None) -> None:
    setup_server(verbose, logs, max_rounds, cache)

    port = port or 8000
    config = Config()
    config.bind = [f"localhost:{port}"]
    asyncio.run(serve(app, config)) # type: ignore
