from typing import Annotated, Any, Dict, List
from eth_account import Account
from eth_account.signers.local import LocalAccount
from gnosis.safe.api.base_api import SafeAPIException
from fastapi import APIRouter, FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback

from autotx import models, setup
from autotx import db
from autotx.AutoTx import AutoTx, Config as AutoTxConfig
from autotx.intents import Intent
from autotx.transactions import Transaction
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

autotx_params: AutoTxParams = AutoTxParams(verbose=False, logs=None, cache=False, max_rounds=200, is_dev=False)

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

def load_config_for_user(app_id: str, user_id: str, address: str, chain_id: int) -> AppConfig:
    agent_private_key = db.get_agent_private_key(app_id, user_id)

    if not agent_private_key:
        raise HTTPException(status_code=400, detail="User not found")

    agent = Account.from_key(agent_private_key)

    app_config = AppConfig.load(smart_account_addr=address, subsidized_chain_id=chain_id, agent=agent)

    return app_config

def authorize_app_and_user(authorization: str | None, user_id: str) -> tuple[models.App, models.AppUser]:
    app = authorize(authorization)
    app_user = db.get_app_user(app.id, user_id)

    if not app_user:
        raise HTTPException(status_code=400, detail="User not found")

    return (app, app_user)

async def build_transactions(app_id: str, user_id: str, chain_id: int, address: str, task: models.Task) -> List[Transaction]:
    if task.running:
        raise HTTPException(status_code=400, detail="Task is still running")

    app_config = load_config_for_user(app_id, user_id, address, chain_id)

    if task.intents is None or len(task.intents) == 0:
        return []

    transactions: list[Transaction] = []

    for intent in task.intents:
        transactions.extend(await intent.build_transactions(app_config.web3, app_config.network_info, app_config.manager.address))

    return transactions

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
    
    app_config = AppConfig.load(smart_account_addr=task.address, subsidized_chain_id=task.chain_id)

    wallet: SmartWallet
    if autotx_params.is_dev:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, tasks)
    else:
        wallet = ApiSmartWallet(app_config.web3, app_config.manager, tasks)

    created_task: models.Task = tasks.start(prompt, wallet.address.hex, app_config.network_info.chain_id.value, app_user.id)
    task_id = created_task.id
    wallet.task_id = task_id

    try:
        (get_llm_config, agents, logs_dir) = setup.setup_agents(autotx_params.logs, cache=autotx_params.cache)

        def on_notify_user(message: str) -> None:
            task = tasks.get(task_id)
            if task is None:
                raise Exception("Task not found: " + task_id)

            task.messages.append(message)
            tasks.update(task)

        autotx = AutoTx(
            app_config.web3,
            wallet,
            app_config.network_info,
            agents,
            AutoTxConfig(verbose=autotx_params.verbose, get_llm_config=get_llm_config, logs_dir=logs_dir, max_rounds=autotx_params.max_rounds),
            on_notify_user=on_notify_user
        )

        async def run_task() -> None:
            try: 
                await autotx.a_run(prompt, non_interactive=True)
            except Exception as e:
                task = tasks.get(task_id)
                if task is None:
                    raise Exception("Task not found: " + task_id)

                task.messages.append(str(e))
                task.error = traceback.format_exc()
                task.running = False
                tasks.update(task)
                raise e
            tasks.stop(task_id)

        background_tasks.add_task(run_task)

        return created_task
    except Exception as e:
        created_task.error = traceback.format_exc()
        created_task.running = False
        tasks.update(created_task)
        raise e

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

    if task.chain_id != chain_id:
        raise HTTPException(status_code=400, detail="Chain ID does not match task")

    transactions = await build_transactions(app.id, user_id, chain_id, address, task)

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

    if task.chain_id != chain_id:
        raise HTTPException(status_code=400, detail="Chain ID does not match task")
    
    transactions = await build_transactions(app.id, app_user.user_id, chain_id, address, task)

    if len(transactions) == 0:
        raise HTTPException(status_code=400, detail="No transactions to send")

    submitted_batch_id = db.save_transactions(app.id, address, chain_id, app_user.id, task_id, transactions)

    return PreparedTransactionsDto(batch_id=submitted_batch_id, transactions=transactions)

@app_router.post("/api/v1/tasks/{task_id}/transactions")
def send_transactions(
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
        app_config = load_config_for_user(app.id, user_id, address, chain_id)

        app_config.manager.send_multisend_tx_batch(
            transactions,
            require_approval=False,
        )
    except SafeAPIException as e:
        if "is not an owner or delegate" in str(e):
            raise HTTPException(status_code=400, detail="Agent is not an owner or delegate")
        else:
            raise e
        
    db.submit_transactions(app.id, app_user.id, batch_id)

    return f"https://app.safe.global/transactions/queue?safe={CHAIN_ID_TO_SHORT_NAME[str(chain_id)]}:{address}"

@app_router.get("/api/v1/networks", response_model=List[models.SupportedNetwork])
def get_supported_networks() -> list[models.SupportedNetwork]:
    return [
        models.SupportedNetwork(name=config.network_name, chain_id=chain_id)
        for chain_id, config in SUPPORTED_NETWORKS_CONFIGURATION_MAP.items()
    ]

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
        AppConfig.load(check_valid_safe=check_valid_safe) # Loading the configuration deploys the dev wallet in dev mode

    global autotx_params
    autotx_params = AutoTxParams(
        verbose=verbose, 
        logs=logs,
        cache=cache,
        max_rounds=max_rounds, 
        is_dev=is_dev,
    )