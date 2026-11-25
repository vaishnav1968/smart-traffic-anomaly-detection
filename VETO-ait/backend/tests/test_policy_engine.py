import pytest
from backend.app.core.policy_engine import PolicyEngine
from backend.app.models.events import DecisionType, RiskLevel

@pytest.fixture
def policy_engine():
    return PolicyEngine("configs/policies.yaml")

def test_safe_read_operation_is_allowed(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="read_file",
        target_resource="project_data.txt",
        parameters={"path": "project_data.txt"}
    )
    assert decision == DecisionType.ALLOW
    assert risk == RiskLevel.LOW
    assert "project file" in reason.lower()

def test_directory_listing_is_allowed(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="list_directory",
        target_resource=".",
        parameters={}
    )
    assert decision == DecisionType.ALLOW
    assert risk == RiskLevel.LOW

def test_sensitive_file_deletion_requires_review(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="delete_file",
        target_resource="system_config.json",
        parameters={"path": "system_config.json"}
    )
    assert decision == DecisionType.REVIEW
    assert risk == RiskLevel.HIGH
    assert "RULE-REVIEW-FILE-DELETION" in rule_id

def test_sensitive_config_modification_requires_review(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="write_file",
        target_resource="system_config.json",
        parameters={"path": "system_config.json", "content": "{}"}
    )
    assert decision == DecisionType.REVIEW
    assert risk == RiskLevel.HIGH

def test_honeytoken_access_is_vetoed(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="read_file",
        target_resource=".env.decoy",
        parameters={"path": ".env.decoy"}
    )
    assert decision == DecisionType.VETO
    assert risk == RiskLevel.CRITICAL
    assert "honeytoken" in reason.lower()

def test_prohibited_command_is_vetoed(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="execute_command",
        target_resource="rm -rf /",
        parameters={"command": "rm -rf /"}
    )
    assert decision == DecisionType.VETO
    assert risk == RiskLevel.CRITICAL
    assert "RULE-VETO-PROHIBITED-COMMANDS" in rule_id

def test_path_traversal_is_vetoed(policy_engine):
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="read_file",
        target_resource="../../etc/shadow",
        parameters={"path": "../../etc/shadow"}
    )
    assert decision == DecisionType.VETO
    assert risk == RiskLevel.CRITICAL
    assert "RULE-VETO-PATH-TRAVERSAL" in rule_id

def test_policy_engine_failure_fails_closed(policy_engine):
    # Corrupt policy doc in memory to simulate runtime error
    policy_engine.policy_doc = None
    policy_engine.policy_path = "/nonexistent/path/corrupt.yaml"
    decision, risk, reason, rule_id = policy_engine.evaluate(
        operation="read_file",
        target_resource="anything",
        parameters={}
    )
    assert decision == DecisionType.VETO
    assert risk == RiskLevel.CRITICAL
    assert "FAIL-CLOSED" in reason
