import pytest
from pathlib import Path
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

@pytest.mark.asyncio
async def test_all_three_demo_scenarios(tmp_path, monkeypatch):
    test_db = tmp_path / "test_demo_audit.db"
    monkeypatch.setattr("backend.app.database.db.get_db_path", lambda: test_db)
    monkeypatch.setattr("backend.app.database.repository.get_db_path", lambda: test_db)

    await init_db()
    repo = AuditRepository()
    audit_logger = AuditLogger(repository=repo)
    honeytoken_detector = HoneytokenDetector(repository=repo)
    egress_controller = EgressController(honeytoken_detector=honeytoken_detector)
    mcp_verifier = MCPIntegrityVerifier()
    policy_engine = PolicyEngine()
    execution_manager = ExecutionManager()

    serial_manager = SerialManager()
    serial_manager.is_simulation = True
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

    runner = DemoRunner(
        interception_proxy=proxy,
        mcp_verifier=mcp_verifier,
        repository=repo
    )

    # 1. Run Demo 1
    demo1_res = await runner.run_scenario_1()
    assert demo1_res["enforcement_successful"] is True
    assert "HONEYTOKEN DETECTED" in demo1_res["outcome"]

    # 2. Run Demo 2
    demo2_res = await runner.run_scenario_2()
    assert demo2_res["enforcement_successful"] is True
    assert "MCP INTEGRITY VIOLATION" in demo2_res["outcome"]

    # 3. Run Demo 3 (with simulated rejection)
    demo3_res = await runner.run_scenario_3(auto_simulate_rejection=True)
    assert demo3_res["enforcement_successful"] is True
    assert demo3_res["file_intact"] is True
    assert "REJECTED" in demo3_res["outcome"]

    # 4. Verify Audit Chain across all recorded demo events
    chain_check = await audit_logger.verify_chain()
    assert chain_check["valid"] is True
    assert chain_check["total_events"] > 0
