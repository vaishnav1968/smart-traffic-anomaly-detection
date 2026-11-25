import os
import aiosqlite
import pytest
from backend.app.database.db import init_db, get_db_path
from backend.app.database.repository import AuditRepository
from backend.app.security.audit_logger import AuditLogger
from backend.app.models.events import SecurityEventCreate, RiskLevel, DecisionType, ExecutionStatus

@pytest.mark.asyncio
async def test_audit_hash_chain_creation_and_verification(tmp_path, monkeypatch):
    test_db = tmp_path / "test_audit.db"
    monkeypatch.setattr("backend.app.database.db.get_db_path", lambda: test_db)
    monkeypatch.setattr("backend.app.database.repository.get_db_path", lambda: test_db)

    await init_db()
    repo = AuditRepository()
    logger = AuditLogger(repository=repo)

    # Log 3 events
    e1 = await logger.log_event(SecurityEventCreate(
        agent_id="AGENT-1",
        session_id="SESS-1",
        operation="read_file",
        target_resource="project_data.txt",
        risk_level=RiskLevel.LOW,
        decision=DecisionType.ALLOW,
        policy_reason="Allowed read",
        execution_outcome=ExecutionStatus.EXECUTED,
        parameters={"path": "project_data.txt"}
    ))

    e2 = await logger.log_event(SecurityEventCreate(
        agent_id="AGENT-1",
        session_id="SESS-1",
        operation="delete_file",
        target_resource="system_config.json",
        risk_level=RiskLevel.HIGH,
        decision=DecisionType.REVIEW,
        policy_reason="Human Review required",
        execution_outcome=ExecutionStatus.PENDING_APPROVAL,
        parameters={"path": "system_config.json"}
    ))

    e3 = await logger.log_event(SecurityEventCreate(
        agent_id="AGENT-1",
        session_id="SESS-1",
        operation="read_file",
        target_resource=".env.decoy",
        risk_level=RiskLevel.CRITICAL,
        decision=DecisionType.VETO,
        policy_reason="Honeytoken detected",
        execution_outcome=ExecutionStatus.BLOCKED,
        parameters={"path": ".env.decoy"}
    ))

    # Verify chain intact
    res = await logger.verify_chain()
    assert res["valid"] is True
    assert res["total_events"] == 3

    # Now tamper with event 2 in the SQLite database directly
    async with aiosqlite.connect(test_db) as db:
        await db.execute(
            "UPDATE security_events SET policy_reason = 'TAMPERED REASON' WHERE event_id = ?",
            (e2.event_id,)
        )
        await db.commit()

    # Verify chain detects tampering
    tamper_res = await logger.verify_chain()
    assert tamper_res["valid"] is False
    assert tamper_res["tampered_event_id"] == e2.event_id
    assert "Tampering detected" in tamper_res["message"]
