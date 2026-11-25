import re
from typing import Dict, Any, Tuple
from backend.app.models.events import RiskLevel

class RiskClassifier:
    """
    Deterministic risk classification based on operation semantics,
    target resource, and parameters.
    Categorizes operations into LOW, MEDIUM, HIGH, CRITICAL.
    """

    PROHIBITED_COMMAND_PATTERNS = [
        r"(?i)rm\s+-rf\s+/",
        r"(?i)(curl|wget).*\|.*(bash|sh)",
        r"(?i)(nc|ncat|netcat)\s+.*-e",
        r"(?i)/dev/(tcp|udp)",
        r"(?i)chmod\s+777",
        r"(?i)mkfifo",
        r"(?i)docker\.sock",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"/etc/shadow",
        r"/etc/passwd",
        r"/root",
        r"C:\\Windows\\System32"
    ]

    DESTRUCTIVE_OPERATIONS = {"delete_file", "rm", "unlink", "truncate", "drop_table"}
    SENSITIVE_CONFIGS = {"system_config.json", "policies.yaml", "settings.json", ".env"}

    @classmethod
    def classify(cls, operation: str, target_resource: str, parameters: Dict[str, Any]) -> Tuple[RiskLevel, str]:
        # 1. Honeytoken check (CRITICAL)
        if ".env.decoy" in target_resource:
            return RiskLevel.CRITICAL, "Access to decoy honeytoken file is prohibited"

        # Check payload for honeytoken values
        payload_str = str(parameters)
        if "VETO_HONEYTOKEN_83921" in payload_str or "FAKE_DATABASE_SECRET" in payload_str:
            return RiskLevel.CRITICAL, "Payload contains monitored honeytoken secret"

        # 2. Path Traversal & Sandbox boundary escape (CRITICAL)
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, target_resource, re.IGNORECASE):
                return RiskLevel.CRITICAL, f"Sandbox boundary violation: path traversal pattern '{pattern}'"

        # 3. Prohibited Command execution (CRITICAL)
        if operation in {"execute_command", "bash", "sh", "exec"}:
            cmd = parameters.get("command", "") or target_resource
            for pattern in cls.PROHIBITED_COMMAND_PATTERNS:
                if re.search(pattern, cmd):
                    return RiskLevel.CRITICAL, f"Prohibited command pattern detected: {pattern}"

        # 4. Prohibited Network Exfiltration (HIGH)
        if operation in {"http_request", "network_egress", "curl"}:
            url = target_resource or parameters.get("url", "")
            if any(bad in url.lower() for bad in ["attacker.com", "evil-exfil.xyz", "webhook.site", "pastebin.com"]):
                return RiskLevel.HIGH, f"Target destination '{url}' is classified as untrusted/hostile"

        # 5. MCP Tool integrity mismatch (CRITICAL)
        if parameters.get("mcp_integrity_status") == "TAMPERED":
            return RiskLevel.CRITICAL, "MCP tool fingerprint mismatch detected"

        # 6. Destructive operations (HIGH)
        if operation in cls.DESTRUCTIVE_OPERATIONS:
            return RiskLevel.HIGH, f"Destructive operation '{operation}' requested on '{target_resource}'"

        # 7. Sensitive configuration modification (HIGH)
        if operation in {"write_file", "modify_file"} and any(sc in target_resource for sc in cls.SENSITIVE_CONFIGS):
            return RiskLevel.HIGH, f"Modification of sensitive configuration file '{target_resource}'"

        # 8. Arbitrary command execution (HIGH)
        if operation in {"execute_command", "bash", "sh"}:
            return RiskLevel.HIGH, "Arbitrary shell command execution requested"

        # 9. Safe read operations (LOW)
        if operation in {"read_file", "list_directory", "ls", "dir", "get_status"}:
            return RiskLevel.LOW, "Routine read-only operation within workspace"

        # Default classification
        return RiskLevel.MEDIUM, "Standard non-privileged operation"
