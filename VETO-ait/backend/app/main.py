import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database.db import init_db
from backend.app.database.repository import AuditRepository
from backend.app.security.audit_logger import AuditLogger
from backend.app.security.honeytoken_detector import HoneytokenDetector
from backend.app.security.egress_controller import EgressController
from backend.app.security.mcp_integrity import MCPIntegrityVerifier
from backend.app.security.interception_proxy import InterceptionProxy
from backend.app.hardware.serial_manager import SerialManager
from backend.app.hardware.heartbeat import HardwareHeartbeat
from backend.app.core.policy_engine import PolicyEngine
from backend.app.core.execution_manager import ExecutionManager
from backend.app.core.approval_manager import ApprovalManager
from backend.app.api.demo import DemoRunner
from backend.app.api.routes import router as api_router, set_services, ws_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("veto.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing VETO Zero-Trust Runtime Security Environment...")
    
    # 1. Initialize SQLite Database
    await init_db()
    repo = AuditRepository()
    
    # 2. Initialize Security & Core Components
    audit_logger = AuditLogger(repository=repo)
    honeytoken_detector = HoneytokenDetector(repository=repo)
    egress_controller = EgressController(honeytoken_detector=honeytoken_detector)
    mcp_verifier = MCPIntegrityVerifier()
    policy_engine = PolicyEngine()
    execution_manager = ExecutionManager()

    # 3. Hardware Serial & Heartbeat
    def on_serial_message(msg_type: str, data: dict):
        logger.info(f"Arduino Event: {msg_type} -> {data}")
        asyncio.create_task(ws_manager.broadcast("ARDUINO_MESSAGE", {"type": msg_type, "data": data}))
        
        # Handle physical buttons
        if msg_type == "APPROVE":
            approval_id = data.get("approval_id")
            if approval_id:
                asyncio.create_task(approval_manager.resolve_approval(approval_id, "APPROVED", "ARDUINO_BUTTON"))
        elif msg_type == "REJECT":
            approval_id = data.get("approval_id")
            if approval_id:
                asyncio.create_task(approval_manager.resolve_approval(approval_id, "REJECTED", "ARDUINO_BUTTON"))
        elif msg_type == "ESTOP":
            heartbeat.trigger_emergency_stop()
            approval_manager.cancel_all_pending("EMERGENCY_STOP")
            asyncio.create_task(ws_manager.broadcast("EMERGENCY_STOP_TRIGGERED", {"status": "ACTIVE"}))
        elif msg_type == "PONG":
            nonce = data.get("nonce", "")
            heartbeat.handle_pong(nonce)

    serial_manager = SerialManager(on_message_callback=on_serial_message)

    def on_heartbeat_expired():
        logger.warning("Heartbeat lease expired. Suspending protected operations (FAIL-CLOSED).")
        approval_manager.cancel_all_pending("HEARTBEAT_LEASE_EXPIRED")
        asyncio.create_task(ws_manager.broadcast("HEARTBEAT_EXPIRED", {"status": "FAIL_CLOSED"}))

    heartbeat = HardwareHeartbeat(
        serial_manager=serial_manager,
        on_lease_expired=on_heartbeat_expired
    )

    # 4. Approval Manager & Interception Gateway
    def on_broadcast(event_type: str, data: dict):
        asyncio.create_task(ws_manager.broadcast(event_type, data))

    approval_manager = ApprovalManager(
        repository=repo,
        serial_manager=serial_manager,
        on_broadcast_callback=on_broadcast
    )

    interception_proxy = InterceptionProxy(
        policy_engine=policy_engine,
        approval_manager=approval_manager,
        execution_manager=execution_manager,
        audit_logger=audit_logger,
        honeytoken_detector=honeytoken_detector,
        egress_controller=egress_controller,
        mcp_verifier=mcp_verifier,
        heartbeat=heartbeat
    )

    demo_runner = DemoRunner(
        interception_proxy=interception_proxy,
        mcp_verifier=mcp_verifier,
        repository=repo
    )

    # Wire services to routes
    set_services({
        "repository": repo,
        "audit_logger": audit_logger,
        "honeytoken_detector": honeytoken_detector,
        "egress_controller": egress_controller,
        "mcp_verifier": mcp_verifier,
        "policy_engine": policy_engine,
        "execution_manager": execution_manager,
        "serial_manager": serial_manager,
        "heartbeat": heartbeat,
        "approval_manager": approval_manager,
        "interception_proxy": interception_proxy,
        "demo_runner": demo_runner
    })

    # Start background loops
    await serial_manager.start()
    await heartbeat.start()

    logger.info("VETO Security Services online and enforcing zero-trust policies.")
    yield

    # Shutdown
    logger.info("Shutting down VETO Security Services...")
    await heartbeat.stop()
    await serial_manager.stop()

app = FastAPI(
    title="VETO Runtime Security Platform",
    description="Zero-Trust Runtime Security for Autonomous AI Agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming ping or messages if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Include API Router
app.include_router(api_router)

# Mount frontend build if available
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
