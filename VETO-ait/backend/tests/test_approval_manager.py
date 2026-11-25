import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from backend.app.models.approvals import ApprovalRequest
from backend.app.core.approval_manager import ApprovalManager
from backend.app.database.repository import AuditRepository
from backend.app.database.db import init_db
from backend.app.hardware.serial_manager import SerialManager

@pytest.mark.asyncio
async def test_approval_binding_and_resolution(tmp_path, monkeypatch):
    test_db = tmp_path / "test_approvals.db"
    monkeypatch.setattr("backend.app.database.db.get_db_path", lambda: test_db)
    monkeypatch.setattr("backend.app.database.repository.get_db_path", lambda: test_db)

    await init_db()
    repo = AuditRepository()
    serial_mgr = SerialManager()
    serial_mgr.is_simulation = True

    mgr = ApprovalManager(repository=repo, serial_manager=serial_mgr)

    # Compute action hash
    action_hash = mgr.compute_action_hash(
        session_id="SESS-01",
        operation="delete_file",
        target_resource="system_config.json",
        parameters={"path": "system_config.json"}
    )
    assert len(action_hash) == 64

    # Background resolver task to simulate human clicking approve
    async def approve_shortly():
        await asyncio.sleep(0.1)
        approvals = await repo.get_approvals(status="PENDING")
        if approvals:
            await mgr.resolve_approval(approvals[0].id, "APPROVED", "DASHBOARD")

    asyncio.create_task(approve_shortly())

    is_approved = await mgr.request_human_approval(
        session_id="SESS-01",
        agent_id="AGENT-01",
        operation="delete_file",
        target_resource="system_config.json",
        parameters={"path": "system_config.json"},
        timeout_seconds=5
    )
    assert is_approved is True

@pytest.mark.asyncio
async def test_approval_rejection_prevents_execution(tmp_path, monkeypatch):
    test_db = tmp_path / "test_approvals_rej.db"
    monkeypatch.setattr("backend.app.database.db.get_db_path", lambda: test_db)
    monkeypatch.setattr("backend.app.database.repository.get_db_path", lambda: test_db)

    await init_db()
    repo = AuditRepository()
    serial_mgr = SerialManager()
    serial_mgr.is_simulation = True

    mgr = ApprovalManager(repository=repo, serial_manager=serial_mgr)

    async def reject_shortly():
        await asyncio.sleep(0.1)
        approvals = await repo.get_approvals(status="PENDING")
        if approvals:
            await mgr.resolve_approval(approvals[0].id, "REJECTED", "ARDUINO_BUTTON")

    asyncio.create_task(reject_shortly())

    is_approved = await mgr.request_human_approval(
        session_id="SESS-01",
        agent_id="AGENT-01",
        operation="delete_file",
        target_resource="system_config.json",
        parameters={"path": "system_config.json"},
        timeout_seconds=5
    )
    assert is_approved is False
