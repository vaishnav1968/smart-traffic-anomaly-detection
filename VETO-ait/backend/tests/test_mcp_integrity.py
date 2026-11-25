import pytest
from backend.app.security.mcp_integrity import MCPIntegrityVerifier

def test_mcp_original_tool_passes_verification():
    verifier = MCPIntegrityVerifier()
    # Baseline read_file
    is_valid, msg, details = verifier.verify_tool_integrity("read_file")
    assert is_valid is True
    assert details["status"] == "VERIFIED"

def test_mcp_tampered_tool_fails_verification():
    verifier = MCPIntegrityVerifier()
    tool_name = "read_file"
    
    # Tamper the tool
    verifier.simulate_tampering(tool_name)
    
    is_valid, msg, details = verifier.verify_tool_integrity(tool_name)
    assert is_valid is False
    assert details["status"] == "TAMPERED"
    assert "mismatch" in msg.lower()

def test_mcp_reapproval_restores_verification():
    verifier = MCPIntegrityVerifier()
    tool_name = "read_file"
    
    verifier.simulate_tampering(tool_name)
    is_valid, _, _ = verifier.verify_tool_integrity(tool_name)
    assert is_valid is False

    # Admin explicitly re-approves
    verifier.approve_tool_fingerprint(tool_name)
    is_valid_after, _, details_after = verifier.verify_tool_integrity(tool_name)
    assert is_valid_after is True
    assert details_after["status"] == "VERIFIED"
