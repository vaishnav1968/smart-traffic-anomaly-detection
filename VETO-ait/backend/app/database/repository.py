import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import aiosqlite
from backend.app.database.db import get_db_path
from backend.app.models.events import SecurityEvent, ThreatIncident, RiskLevel, DecisionType, ExecutionStatus
from backend.app.models.approvals import ApprovalRequest

class AuditRepository:
    def __init__(self):
        self.db_path = get_db_path()

    async def get_latest_event_hash(self) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT event_hash FROM security_events ORDER BY rowid DESC LIMIT 1")
            row = await cursor.fetchone()
            if row:
                return row[0]
            # Genesis block hash
            return "0000000000000000000000000000000000000000000000000000000000000000"

    async def save_security_event(self, event: SecurityEvent) -> SecurityEvent:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO security_events (
                    event_id, timestamp, agent_id, session_id, operation,
                    target_resource, risk_level, decision, policy_reason,
                    execution_outcome, parameters, previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.agent_id,
                    event.session_id,
                    event.operation,
                    event.target_resource,
                    event.risk_level.value,
                    event.decision.value,
                    event.policy_reason,
                    event.execution_outcome.value,
                    json.dumps(event.parameters, sort_keys=True),
                    event.previous_hash,
                    event.event_hash
                )
            )
            await db.commit()
        return event

    async def get_security_events(self, limit: int = 100, offset: int = 0) -> List[SecurityEvent]:
        events = []
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM security_events ORDER BY rowid DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            for r in rows:
                events.append(SecurityEvent(
                    event_id=r[0],
                    timestamp=datetime.fromisoformat(r[1]),
                    agent_id=r[2],
                    session_id=r[3],
                    operation=r[4],
                    target_resource=r[5],
                    risk_level=RiskLevel(r[6]),
                    decision=DecisionType(r[7]),
                    policy_reason=r[8],
                    execution_outcome=ExecutionStatus(r[9]),
                    parameters=json.loads(r[10]),
                    previous_hash=r[11],
                    event_hash=r[12]
                ))
        return events

    async def get_event_by_id(self, event_id: str) -> Optional[SecurityEvent]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM security_events WHERE event_id = ?", (event_id,))
            r = await cursor.fetchone()
            if not r:
                return None
            return SecurityEvent(
                event_id=r[0],
                timestamp=datetime.fromisoformat(r[1]),
                agent_id=r[2],
                session_id=r[3],
                operation=r[4],
                target_resource=r[5],
                risk_level=RiskLevel(r[6]),
                decision=DecisionType(r[7]),
                policy_reason=r[8],
                execution_outcome=ExecutionStatus(r[9]),
                parameters=json.loads(r[10]),
                previous_hash=r[11],
                event_hash=r[12]
            )

    async def get_all_events_chronological(self) -> List[SecurityEvent]:
        events = []
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM security_events ORDER BY rowid ASC")
            rows = await cursor.fetchall()
            for r in rows:
                events.append(SecurityEvent(
                    event_id=r[0],
                    timestamp=datetime.fromisoformat(r[1]),
                    agent_id=r[2],
                    session_id=r[3],
                    operation=r[4],
                    target_resource=r[5],
                    risk_level=RiskLevel(r[6]),
                    decision=DecisionType(r[7]),
                    policy_reason=r[8],
                    execution_outcome=ExecutionStatus(r[9]),
                    parameters=json.loads(r[10]),
                    previous_hash=r[11],
                    event_hash=r[12]
                ))
        return events

    # Approvals
    async def save_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO approvals (
                    id, session_id, agent_id, operation, target_resource,
                    action_hash, parameters, created_at, expires_at, status,
                    resolved_by, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval.id,
                    approval.session_id,
                    approval.agent_id,
                    approval.operation,
                    approval.target_resource,
                    approval.action_hash,
                    json.dumps(approval.parameters, sort_keys=True),
                    approval.created_at.isoformat(),
                    approval.expires_at.isoformat(),
                    approval.status,
                    approval.resolved_by,
                    approval.resolved_at.isoformat() if approval.resolved_at else None
                )
            )
            await db.commit()
        return approval

    async def update_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE approvals SET
                    status = ?, resolved_by = ?, resolved_at = ?
                WHERE id = ?
                """,
                (
                    approval.status,
                    approval.resolved_by,
                    approval.resolved_at.isoformat() if approval.resolved_at else None,
                    approval.id
                )
            )
            await db.commit()
        return approval

    async def get_approvals(self, status: Optional[str] = None) -> List[ApprovalRequest]:
        approvals = []
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                cursor = await db.execute("SELECT * FROM approvals WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor = await db.execute("SELECT * FROM approvals ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            for r in rows:
                approvals.append(ApprovalRequest(
                    id=r[0],
                    session_id=r[1],
                    agent_id=r[2],
                    operation=r[3],
                    target_resource=r[4],
                    action_hash=r[5],
                    parameters=json.loads(r[6]),
                    created_at=datetime.fromisoformat(r[7]),
                    expires_at=datetime.fromisoformat(r[8]),
                    status=r[9],
                    resolved_by=r[10],
                    resolved_at=datetime.fromisoformat(r[11]) if r[11] else None
                ))
        return approvals

    async def get_approval_by_id(self, approval_id: str) -> Optional[ApprovalRequest]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,))
            r = await cursor.fetchone()
            if not r:
                return None
            return ApprovalRequest(
                id=r[0],
                session_id=r[1],
                agent_id=r[2],
                operation=r[3],
                target_resource=r[4],
                action_hash=r[5],
                parameters=json.loads(r[6]),
                created_at=datetime.fromisoformat(r[7]),
                expires_at=datetime.fromisoformat(r[8]),
                status=r[9],
                resolved_by=r[10],
                resolved_at=datetime.fromisoformat(r[11]) if r[11] else None
            )

    # Threats
    async def save_threat(self, threat: ThreatIncident) -> ThreatIncident:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO threat_incidents (
                    id, timestamp, threat_type, severity, description, details, blocked
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    threat.id,
                    threat.timestamp.isoformat(),
                    threat.threat_type,
                    threat.severity.value,
                    threat.description,
                    json.dumps(threat.details, sort_keys=True),
                    1 if threat.blocked else 0
                )
            )
            await db.commit()
        return threat

    async def get_threats(self, limit: int = 50) -> List[ThreatIncident]:
        threats = []
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM threat_incidents ORDER BY rowid DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            for r in rows:
                threats.append(ThreatIncident(
                    id=r[0],
                    timestamp=datetime.fromisoformat(r[1]),
                    threat_type=r[2],
                    severity=RiskLevel(r[3]),
                    description=r[4],
                    details=json.loads(r[5]),
                    blocked=bool(r[6])
                ))
        return threats

    # Summary Stats
    async def get_system_stats(self) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            c = await db.execute("SELECT count(*) FROM security_events")
            total_ops = (await c.fetchone())[0]

            c = await db.execute("SELECT count(*) FROM security_events WHERE decision = 'ALLOW'")
            allowed_ops = (await c.fetchone())[0]

            c = await db.execute("SELECT count(*) FROM security_events WHERE decision = 'VETO'")
            blocked_ops = (await c.fetchone())[0]

            c = await db.execute("SELECT count(*) FROM approvals WHERE status = 'PENDING'")
            pending_approvals = (await c.fetchone())[0]

            c = await db.execute("SELECT count(*) FROM threat_incidents")
            threats_count = (await c.fetchone())[0]

            return {
                "total_operations": total_ops,
                "allowed_operations": allowed_ops,
                "blocked_operations": blocked_ops,
                "pending_approvals": pending_approvals,
                "security_incidents": threats_count
            }
