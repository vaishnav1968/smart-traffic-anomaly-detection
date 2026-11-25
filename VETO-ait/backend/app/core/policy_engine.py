import re
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from backend.app.config import settings
from backend.app.models.events import RiskLevel, DecisionType
from backend.app.models.policies import PolicyDocument, PolicyRule
from backend.app.core.risk_classifier import RiskClassifier

class PolicyEngine:
    def __init__(self, policy_path: Optional[str] = None):
        self.policy_path = policy_path or settings.POLICIES_FILE
        self.policy_doc: Optional[PolicyDocument] = None
        self.load_policy()

    def load_policy(self) -> PolicyDocument:
        p = Path(self.policy_path)
        if not p.is_absolute():
            p = settings.BASE_DIR / p
        
        if not p.exists():
            raise FileNotFoundError(f"Policy file not found at: {p}")
            
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        self.policy_doc = PolicyDocument(**data)
        # Sort rules by priority (ascending: 1 is highest priority)
        self.policy_doc.rules.sort(key=lambda r: r.priority)
        return self.policy_doc

    def evaluate(
        self,
        operation: str,
        target_resource: str,
        parameters: Dict[str, Any]
    ) -> Tuple[DecisionType, RiskLevel, str, str]:
        """
        Deterministically evaluates an intercepted operation against configurable policies.
        Returns: (decision, risk_level, reason, matched_rule_id)
        
        Fail-Closed Principle: If an error or unhandled state occurs, returns VETO immediately.
        """
        try:
            if not self.policy_doc:
                self.load_policy()

            assert self.policy_doc is not None

            # First, classify inherent risk
            inherent_risk, inherent_reason = RiskClassifier.classify(
                operation=operation,
                target_resource=target_resource,
                parameters=parameters
            )

            # Check explicit rules in priority order
            for rule in self.policy_doc.rules:
                if self._matches_rule(rule, operation, target_resource, parameters):
                    return rule.decision, rule.risk_level, rule.reason, rule.id

            # Fallback mapping based on risk tier
            tier_decision_str = self.policy_doc.risk_tier_mapping.get(inherent_risk.value, "VETO")
            decision = DecisionType(tier_decision_str)
            return decision, inherent_risk, f"Fallback risk evaluation ({inherent_risk.value}): {inherent_reason}", "FALLBACK-RISK-TIER"

        except Exception as e:
            # FAIL-CLOSED BEHAVIOR: Never allow operations if policy engine fails
            return DecisionType.VETO, RiskLevel.CRITICAL, f"FAIL-CLOSED: Policy engine evaluation error: {str(e)}", "SYSTEM-FAIL-CLOSED"

    def _matches_rule(
        self,
        rule: PolicyRule,
        operation: str,
        target_resource: str,
        parameters: Dict[str, Any]
    ) -> bool:
        cond = rule.condition

        # Check operation type
        if cond.operation_types and operation not in cond.operation_types:
            return False

        # Check target resource contains
        if cond.target_resource_contains:
            matches_contains = any(sub in target_resource for sub in cond.target_resource_contains)
            if not matches_contains:
                return False

        # Check target resource regex
        if cond.target_resource_regex:
            if not re.search(cond.target_resource_regex, target_resource):
                return False

        # Check command regex (for execute_command)
        if cond.command_regex:
            cmd = parameters.get("command", "") or target_resource
            matches_cmd = any(re.search(pat, cmd) for pat in cond.command_regex)
            if not matches_cmd:
                return False

        # Check payload contains
        if cond.payload_contains:
            param_str = str(parameters)
            matches_payload = any(pat in param_str for pat in cond.payload_contains)
            if not matches_payload:
                return False

        # Check tool names
        if cond.tool_names and parameters.get("tool_name", operation) not in cond.tool_names:
            return False

        # Check MCP integrity status
        if cond.mcp_integrity_status:
            if parameters.get("mcp_integrity_status") != cond.mcp_integrity_status:
                return False

        # Check exclude contains
        if cond.exclude_contains:
            if any(exc in target_resource for exc in cond.exclude_contains):
                return False

        return True
