from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ApprovalRequest(BaseModel):
    id: str
    session_id: str
    agent_id: str
    operation: str
    target_resource: str
    action_hash: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    expires_at: datetime
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXPIRED, CANCELLED
    resolved_by: Optional[str] = None  # ARDUINO, DASHBOARD, SYSTEM_TIMEOUT, EMERGENCY_STOP
    resolved_at: Optional[datetime] = None

class ApprovalDecisionRequest(BaseModel):
    decision: str  # APPROVED, REJECTED
    resolved_by: str = "DASHBOARD"
