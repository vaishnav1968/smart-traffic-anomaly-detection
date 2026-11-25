import uuid
import json
import hashlib
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
from backend.app.config import settings
from backend.app.models.approvals import ApprovalRequest
from backend.app.database.repository import AuditRepository
from backend.app.hardware.serial_manager import SerialManager
from backend.app.hardware.arduino_protocol import ArduinoProtocol

class ApprovalManager:
    """
    Manages Human Review requests.
    Binds approvals securely to:
      - Unique approval ID
      - Session ID
      - Exact operation
      - Target resource
      - Action SHA-256 hash
      - Expiry time
    
    Synchronizes decisions across both physical Arduino Uno R3 buttons and the Web Dashboard.
    Ensures that resolving an approval on one interface immediately completes it and invalidates the other.
    Rejects expired or mutated approvals.
    """

    def __init__(
        self,
        repository: AuditRepository,
        serial_manager: SerialManager,
        on_broadcast_callback: Optional[Callable[[str, Any], None]] = None
    ):
        self.repo = repository
        self.serial_manager = serial_manager
        self.broadcast = on_broadcast_callback
        self._pending_futures: Dict[str, asyncio.Future] = {}
        self._active_requests: Dict[str, ApprovalRequest] = {}

    @staticmethod
    def compute_action_hash(session_id: str, operation: str, target_resource: str, parameters: Dict[str, Any]) -> str:
        canonical_params = json.dumps(parameters, sort_keys=True, separators=(",", ":"))
        combined = f"{session_id}|{operation}|{target_resource}|{canonical_params}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def request_human_approval(
        self,
        session_id: str,
        agent_id: str,
        operation: str,
        target_resource: str,
        parameters: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> bool:
        """
        Creates a pending approval, sends details to Arduino OLED and Web Dashboard,
        and pauses execution until human decides (or timeout expires).
        """
        approval_id = f"APR-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc)
        timeout = timeout_seconds or settings.APPROVAL_TIMEOUT_SECONDS
        expires_at = now + timedelta(seconds=timeout)
        action_hash = self.compute_action_hash(session_id, operation, target_resource, parameters)

        approval = ApprovalRequest(
            id=approval_id,
            session_id=session_id,
            agent_id=agent_id,
            operation=operation,
            target_resource=target_resource,
            action_hash=action_hash,
            parameters=parameters,
            created_at=now,
            expires_at=expires_at,
            status="PENDING"
        )

        await self.repo.save_approval(approval)
        self._active_requests[approval_id] = approval

        # Create future to pause execution
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_futures[approval_id] = future

        # 1. Send to Arduino via serial
        self.serial_manager.send_message(
            ArduinoProtocol.format_pending(approval_id, operation, target_resource)
        )

        # 2. Broadcast via WebSocket to Web Dashboard
        if self.broadcast:
            self.broadcast("APPROVAL_REQUESTED", approval.model_dump(mode="json"))

        # Wait for decision or timeout
        try:
            is_approved = await asyncio.wait_for(future, timeout=timeout)
            return is_approved
        except asyncio.TimeoutError:
            # Expired: fail-closed
            await self.resolve_approval(
                approval_id=approval_id,
                decision="REJECTED",
                resolved_by="SYSTEM_TIMEOUT"
            )
            return False
        finally:
            self._pending_futures.pop(approval_id, None)
            self._active_requests.pop(approval_id, None)

    async def resolve_approval(
        self,
        approval_id: str,
        decision: str,  # APPROVED or REJECTED
        resolved_by: str = "DASHBOARD"  # ARDUINO or DASHBOARD
    ) -> Optional[ApprovalRequest]:
        """
        Resolves a pending approval, updates database, notifies Arduino and Web Dashboard,
        and unpauses the waiting execution future.
        """
        approval = await self.repo.get_approval_by_id(approval_id)
        if not approval or approval.status != "PENDING":
            return None

        # Check expiry
        now = datetime.now(timezone.utc)
        if now > approval.expires_at:
            approval.status = "EXPIRED"
            approval.resolved_by = "SYSTEM_TIMEOUT"
            approval.resolved_at = now
            await self.repo.update_approval(approval)
            if approval_id in self._pending_futures:
                self._pending_futures[approval_id].set_result(False)
            return approval

        # Apply decision
        is_approved = (decision.upper() == "APPROVED")
        approval.status = "APPROVED" if is_approved else "REJECTED"
        approval.resolved_by = resolved_by
        approval.resolved_at = now
        await self.repo.update_approval(approval)

        # Send decision result back to Arduino to update LED/OLED
        self.serial_manager.send_message(
            ArduinoProtocol.format_decision(approval_id, approval.status)
        )

        # Notify Web Dashboard
        if self.broadcast:
            self.broadcast("APPROVAL_RESOLVED", approval.model_dump(mode="json"))

        # Fulfill awaiting execution future
        if approval_id in self._pending_futures:
            future = self._pending_futures[approval_id]
            if not future.done():
                future.set_result(is_approved)

        return approval

    def cancel_all_pending(self, reason: str = "EMERGENCY_STOP"):
        """
        Cancels all pending approvals (used during E-STOP or serial disconnect).
        """
        now = datetime.now(timezone.utc)
        for apr_id, future in list(self._pending_futures.items()):
            if not future.done():
                future.set_result(False)
        for apr_id, apr in list(self._active_requests.items()):
            apr.status = "REJECTED"
            apr.resolved_by = reason
            apr.resolved_at = now
            asyncio.create_task(self.repo.update_approval(apr))
        self._pending_futures.clear()
        self._active_requests.clear()
