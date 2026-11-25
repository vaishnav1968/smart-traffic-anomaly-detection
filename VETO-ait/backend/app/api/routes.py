import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.models.events import SecurityEvent, ThreatIncident
from backend.app.models.approvals import ApprovalRequest, ApprovalDecisionRequest
from backend.app.models.policies import PolicyDocument
from backend.app.database.repository import AuditRepository
from backend.app.security.interception_proxy import InterceptionProxy
from backend.app.security.mcp_integrity import MCPIntegrityVerifier
from backend.app.security.audit_logger import AuditLogger
from backend.app.security.honeytoken_detector import HoneytokenDetector
from backend.app.security.egress_controller import EgressController
from backend.app.core.execution_manager import ExecutionManager
from backend.app.core.approval_manager import ApprovalManager
from backend.app.hardware.serial_manager import SerialManager
from backend.app.hardware.heartbeat import HardwareHeartbeat
from backend.app.core.policy_engine import PolicyEngine
from backend.app.api.demo import DemoRunner

router = APIRouter(prefix="/api")

# Request Models
class InterceptRequest(BaseModel):
    agent_id: str = "AGENT-AUTONOMOUS-01"
    session_id: str = "SESSION-DEFAULT"
    operation: str
    target_resource: str
    parameters: Dict[str, Any] = {}

class EmergencyStopResetRequest(BaseModel):
    admin_token: Optional[str] = None

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: Any):
        msg = json.dumps({"type": event_type, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
        for connection in list(self.active_connections):
            try:
                await connection.send_text(msg)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

# Global Dependency Injectors (set in main.py)
_services: Dict[str, Any] = {}

def _ensure_services():
    global _services
    if not _services:
        repo = AuditRepository()
        audit_logger = AuditLogger(repository=repo)
        honeytoken_detector = HoneytokenDetector(repository=repo)
        egress_controller = EgressController(honeytoken_detector=honeytoken_detector)
        mcp_verifier = MCPIntegrityVerifier()
        policy_engine = PolicyEngine()
        execution_manager = ExecutionManager()
        serial_manager = SerialManager()
        heartbeat = HardwareHeartbeat(serial_manager=serial_manager)
        approval_manager = ApprovalManager(repository=repo, serial_manager=serial_manager)
        proxy = InterceptionProxy(
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
            interception_proxy=proxy,
            mcp_verifier=mcp_verifier,
            repository=repo
        )
        _services = {
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
            "interception_proxy": proxy,
            "demo_runner": demo_runner
        }

def set_services(services: Dict[str, Any]):
    global _services
    _services = services

def get_proxy() -> InterceptionProxy:
    _ensure_services()
    return _services["interception_proxy"]

def get_repo() -> AuditRepository:
    _ensure_services()
    return _services["repository"]

def get_audit_logger() -> AuditLogger:
    _ensure_services()
    return _services["audit_logger"]

def get_mcp() -> MCPIntegrityVerifier:
    _ensure_services()
    return _services["mcp_verifier"]

def get_policy_engine() -> PolicyEngine:
    _ensure_services()
    return _services["policy_engine"]

def get_serial_manager() -> SerialManager:
    _ensure_services()
    return _services["serial_manager"]

def get_heartbeat() -> HardwareHeartbeat:
    _ensure_services()
    return _services["heartbeat"]

def get_demo_runner() -> DemoRunner:
    _ensure_services()
    return _services["demo_runner"]

# ----------------- Status & Stats -----------------
@router.get("/status")
async def get_system_status():
    repo = get_repo()
    serial_mgr = get_serial_manager()
    heartbeat = get_heartbeat()
    proxy = get_proxy()

    stats = await repo.get_system_stats()
    hw_status = serial_mgr.get_status()
    sandbox_status = proxy.execution_manager.get_sandbox_status()

    return {
        "status": "EMERGENCY_STOPPED" if heartbeat.emergency_stop_triggered else ("NOMINAL" if hw_status["connected"] or hw_status["simulation_mode"] else "DEGRADED"),
        "emergency_stop": heartbeat.emergency_stop_triggered,
        "hardware": hw_status,
        "sandbox": sandbox_status,
        "stats": stats,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ----------------- Interception Gateway -----------------
@router.post("/intercept")
async def intercept_agent_call(req: InterceptRequest):
    proxy = get_proxy()
    result = await proxy.intercept_operation(
        agent_id=req.agent_id,
        session_id=req.session_id,
        operation=req.operation,
        target_resource=req.target_resource,
        parameters=req.parameters
    )
    # Broadcast event
    await ws_manager.broadcast("OPERATION_INTERCEPTED", result)
    return result

# ----------------- Events & Audit Trail -----------------
@router.get("/events")
async def get_events(limit: int = 50, offset: int = 0):
    repo = get_repo()
    events = await repo.get_security_events(limit=limit, offset=offset)
    return events

@router.get("/events/{event_id}")
async def get_event_detail(event_id: str):
    repo = get_repo()
    event = await repo.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    return event

@router.get("/audit/verify")
async def verify_audit_chain():
    audit_logger = get_audit_logger()
    result = await audit_logger.verify_chain()
    return result

# ----------------- Approvals -----------------
@router.get("/approvals")
async def get_approvals(status: Optional[str] = None):
    repo = get_repo()
    return await repo.get_approvals(status=status)

@router.post("/approvals/{approval_id}/approve")
async def approve_request(approval_id: str):
    proxy = get_proxy()
    res = await proxy.approval_manager.resolve_approval(
        approval_id=approval_id,
        decision="APPROVED",
        resolved_by="DASHBOARD"
    )
    if not res:
        raise HTTPException(status_code=400, detail="Approval request not found, already resolved, or expired")
    await ws_manager.broadcast("APPROVAL_RESOLVED", res.model_dump(mode="json"))
    return {"success": True, "approval": res}

@router.post("/approvals/{approval_id}/reject")
async def reject_request(approval_id: str):
    proxy = get_proxy()
    res = await proxy.approval_manager.resolve_approval(
        approval_id=approval_id,
        decision="REJECTED",
        resolved_by="DASHBOARD"
    )
    if not res:
        raise HTTPException(status_code=400, detail="Approval request not found, already resolved, or expired")
    await ws_manager.broadcast("APPROVAL_RESOLVED", res.model_dump(mode="json"))
    return {"success": True, "approval": res}

# ----------------- Emergency Stop -----------------
@router.post("/emergency-stop")
async def trigger_emergency_stop():
    heartbeat = get_heartbeat()
    proxy = get_proxy()
    heartbeat.trigger_emergency_stop()
    proxy.approval_manager.cancel_all_pending("EMERGENCY_STOP")
    await ws_manager.broadcast("EMERGENCY_STOP_TRIGGERED", {"status": "ACTIVE"})
    return {"success": True, "status": "EMERGENCY_STOP_TRIGGERED"}

@router.post("/emergency-stop/reset")
async def reset_emergency_stop():
    heartbeat = get_heartbeat()
    heartbeat.reset_emergency_stop()
    await ws_manager.broadcast("EMERGENCY_STOP_RESET", {"status": "NOMINAL"})
    return {"success": True, "status": "NOMINAL"}

# ----------------- Threats -----------------
@router.get("/threats")
async def get_threats(limit: int = 50):
    repo = get_repo()
    return await repo.get_threats(limit=limit)

# ----------------- MCP Integrity -----------------
@router.get("/mcp/integrity")
async def get_mcp_tools():
    mcp = get_mcp()
    return mcp.get_all_tools()

@router.post("/mcp/verify")
async def verify_mcp_tool(tool_name: str):
    mcp = get_mcp()
    is_valid, msg, details = mcp.verify_tool_integrity(tool_name)
    return {"valid": is_valid, "message": msg, "details": details}

@router.post("/mcp/tamper")
async def tamper_mcp_tool(tool_name: str = "read_file"):
    mcp = get_mcp()
    tool = mcp.simulate_tampering(tool_name)
    await ws_manager.broadcast("MCP_TOOL_TAMPERED", tool)
    return {"success": True, "tool": tool}

@router.post("/mcp/approve-fingerprint")
async def approve_mcp_fingerprint(tool_name: str = "read_file"):
    mcp = get_mcp()
    tool = mcp.approve_tool_fingerprint(tool_name)
    await ws_manager.broadcast("MCP_TOOL_APPROVED", tool)
    return {"success": True, "tool": tool}

# ----------------- Policies -----------------
@router.get("/policies")
async def get_policies():
    policy_engine = get_policy_engine()
    return policy_engine.policy_doc

@router.put("/policies")
async def update_policies(policy: PolicyDocument):
    policy_engine = get_policy_engine()
    # Save back to YAML
    import yaml
    p = settings.BASE_DIR / settings.POLICIES_FILE
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(policy.model_dump(), f, sort_keys=False)
    policy_engine.load_policy()
    return {"success": True, "policy": policy}

# ----------------- Hardware Status -----------------
@router.get("/hardware/status")
async def get_hardware_status():
    serial_mgr = get_serial_manager()
    return serial_mgr.get_status()

# ----------------- Demonstrations -----------------
@router.post("/demo/{scenario}/run")
async def run_demo_scenario(scenario: str, simulate_rejection: bool = True):
    runner = get_demo_runner()
    if scenario == "prompt-injection" or scenario == "1":
        res = await runner.run_scenario_1()
    elif scenario == "mcp-tampering" or scenario == "2":
        res = await runner.run_scenario_2()
    elif scenario == "physical-approval" or scenario == "3":
        res = await runner.run_scenario_3(auto_simulate_rejection=simulate_rejection)
    else:
        raise HTTPException(status_code=404, detail="Unknown demonstration scenario")
    
    await ws_manager.broadcast("DEMO_COMPLETED", res)
    return res

# ----------------- Controlled Mock Attacker Endpoint -----------------
@router.post("/mock-attacker/exfiltrate")
async def mock_attacker_exfiltrate(data: Dict[str, Any]):
    return {
        "status": "MOCK_ATTACKER_RECEIVER",
        "received_data": data,
        "warning": "This is a controlled benchmark endpoint."
    }
