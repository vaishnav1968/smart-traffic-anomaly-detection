from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    VETO = "VETO"

class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

class SecurityEvent(BaseModel):
    event_id: str
    timestamp: datetime
    agent_id: str
    session_id: str
    operation: str
    target_resource: str
    risk_level: RiskLevel
    decision: DecisionType
    policy_reason: str
    execution_outcome: ExecutionStatus
    parameters: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str

class SecurityEventCreate(BaseModel):
    agent_id: str
    session_id: str
    operation: str
    target_resource: str
    risk_level: RiskLevel
    decision: DecisionType
    policy_reason: str
    execution_outcome: ExecutionStatus
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ThreatIncident(BaseModel):
    id: str
    timestamp: datetime
    threat_type: str
    severity: RiskLevel
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    blocked: bool = True
