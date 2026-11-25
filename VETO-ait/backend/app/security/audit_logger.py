import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from backend.app.models.events import SecurityEvent, SecurityEventCreate, RiskLevel, DecisionType, ExecutionStatus
from backend.app.database.repository import AuditRepository

class AuditLogger:
    def __init__(self, repository: Optional[AuditRepository] = None):
        self.repo = repository or AuditRepository()

    @staticmethod
    def compute_hash(previous_hash: str, event_payload: Dict[str, Any]) -> str:
        """
        Computes SHA-256 over previous_hash + canonical JSON of event data.
        Canonical JSON ensures deterministic key sorting and whitespace.
        """
        canonical_json = json.dumps(event_payload, sort_keys=True, separators=(",", ":"))
        combined = f"{previous_hash}|{canonical_json}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def log_event(self, event_create: SecurityEventCreate) -> SecurityEvent:
        event_id = f"EVT-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc)
        
        # Get latest chain hash
        prev_hash = await self.repo.get_latest_event_hash()

        # Build payload for hashing
        payload_for_hashing = {
            "event_id": event_id,
            "timestamp": now.isoformat(),
            "agent_id": event_create.agent_id,
            "session_id": event_create.session_id,
            "operation": event_create.operation,
            "target_resource": event_create.target_resource,
            "risk_level": event_create.risk_level.value,
            "decision": event_create.decision.value,
            "policy_reason": event_create.policy_reason,
            "execution_outcome": event_create.execution_outcome.value,
            "parameters": event_create.parameters,
        }

        current_hash = self.compute_hash(prev_hash, payload_for_hashing)

        event = SecurityEvent(
            event_id=event_id,
            timestamp=now,
            agent_id=event_create.agent_id,
            session_id=event_create.session_id,
            operation=event_create.operation,
            target_resource=event_create.target_resource,
            risk_level=event_create.risk_level,
            decision=event_create.decision,
            policy_reason=event_create.policy_reason,
            execution_outcome=event_create.execution_outcome,
            parameters=event_create.parameters,
            previous_hash=prev_hash,
            event_hash=current_hash
        )

        return await self.repo.save_security_event(event)

    async def verify_chain(self) -> Dict[str, Any]:
        """
        Scans all security events in chronological order, recomputing and verifying the SHA-256 hash chain.
        Returns detailed verification status, identifying any tampered record.
        """
        events = await self.repo.get_all_events_chronological()
        if not events:
            return {
                "valid": True,
                "total_events": 0,
                "message": "Audit log is empty. Genesis state intact.",
                "tampered_event_id": None
            }

        expected_prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        for idx, event in enumerate(events):
            # Check previous hash link
            if event.previous_hash != expected_prev_hash:
                return {
                    "valid": False,
                    "total_events": len(events),
                    "verified_up_to_index": idx,
                    "tampered_event_id": event.event_id,
                    "message": f"Hash chain broken at event {event.event_id}. Previous hash mismatch: expected {expected_prev_hash[:16]}..., found {event.previous_hash[:16]}..."
                }

            # Recompute current hash
            payload = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "agent_id": event.agent_id,
                "session_id": event.session_id,
                "operation": event.operation,
                "target_resource": event.target_resource,
                "risk_level": event.risk_level.value,
                "decision": event.decision.value,
                "policy_reason": event.policy_reason,
                "execution_outcome": event.execution_outcome.value,
                "parameters": event.parameters,
            }
            computed_hash = self.compute_hash(event.previous_hash, payload)
            if computed_hash != event.event_hash:
                return {
                    "valid": False,
                    "total_events": len(events),
                    "verified_up_to_index": idx,
                    "tampered_event_id": event.event_id,
                    "message": f"Tampering detected in event {event.event_id}! Payload hash does not match stored hash."
                }

            expected_prev_hash = event.event_hash

        return {
            "valid": True,
            "total_events": len(events),
            "head_hash": expected_prev_hash,
            "message": f"Audit chain verified successfully. {len(events)} events checked. Chain integrity 100% valid."
        }
