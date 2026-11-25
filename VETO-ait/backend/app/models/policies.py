from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.events import RiskLevel, DecisionType

class RuleCondition(BaseModel):
    operation_types: Optional[List[str]] = None
    target_resource_contains: Optional[List[str]] = None
    target_resource_regex: Optional[str] = None
    command_regex: Optional[List[str]] = None
    payload_contains: Optional[List[str]] = None
    tool_names: Optional[List[str]] = None
    mcp_integrity_status: Optional[str] = None
    exclude_contains: Optional[List[str]] = None

class PolicyRule(BaseModel):
    id: str
    priority: int
    description: str
    decision: DecisionType
    risk_level: RiskLevel
    condition: RuleCondition
    reason: str

class NetworkEgressPolicy(BaseModel):
    default_action: str = "VETO"
    allowed_hosts: List[str] = Field(default_factory=list)
    blocked_hosts: List[str] = Field(default_factory=list)

class HoneytokensPolicy(BaseModel):
    files: List[str] = Field(default_factory=list)
    secret_patterns: List[str] = Field(default_factory=list)

class PolicyDocument(BaseModel):
    version: str = "1.0"
    policy_name: str = "veto_default_zero_trust"
    enforcement_mode: str = "strict"
    risk_tier_mapping: Dict[str, str] = Field(default_factory=dict)
    honeytokens: HoneytokensPolicy = Field(default_factory=HoneytokensPolicy)
    network_egress: NetworkEgressPolicy = Field(default_factory=NetworkEgressPolicy)
    rules: List[PolicyRule] = Field(default_factory=list)
