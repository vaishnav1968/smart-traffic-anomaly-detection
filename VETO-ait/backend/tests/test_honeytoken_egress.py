import pytest
from backend.app.security.honeytoken_detector import HoneytokenDetector
from backend.app.security.egress_controller import EgressController

def test_decoy_file_detection():
    detector = HoneytokenDetector()
    detected, msg = detector.check_resource_access(".env.decoy")
    assert detected is True
    assert "Honeytoken" in msg

    detected, msg = detector.check_resource_access("/workspace/.env.decoy")
    assert detected is True

    detected, _ = detector.check_resource_access("project_data.txt")
    assert detected is False

def test_secret_scanner_in_payload():
    detector = HoneytokenDetector()
    payload = {"api_key": "VETO_HONEYTOKEN_83921", "env": "prod"}
    detected, token, desc = detector.scan_payload_for_secrets(payload)
    assert detected is True
    assert token == "VETO_HONEYTOKEN_83921"

    normal_payload = {"api_key": "ordinary_user_token_123"}
    detected, _, _ = detector.scan_payload_for_secrets(normal_payload)
    assert detected is False

def test_egress_controller_blocks_honeytoken_transmission():
    detector = HoneytokenDetector()
    egress = EgressController(detector)
    
    # Attempt exfiltration to allowed host with honeytoken
    permitted, reason, details = egress.inspect_outbound_request(
        url="https://api.github.com/upload",
        payload={"secret": "VETO_HONEYTOKEN_83921"}
    )
    assert permitted is False
    assert "HONEYTOKEN_LEAK" in details["violation"]

def test_egress_controller_blocks_hostile_domains():
    detector = HoneytokenDetector()
    egress = EgressController(detector)

    permitted, reason, details = egress.inspect_outbound_request(
        url="http://attacker.com/collect",
        payload={"normal": "data"}
    )
    assert permitted is False
    assert "PROHIBITED_HOST" in details["violation"]

def test_egress_controller_permits_whitelisted_traffic():
    detector = HoneytokenDetector()
    egress = EgressController(detector)

    permitted, reason, details = egress.inspect_outbound_request(
        url="https://api.weather.gov/forecast",
        payload={"coords": "37.77,-122.41"}
    )
    assert permitted is True
    assert details["status"] == "ALLOWED"
