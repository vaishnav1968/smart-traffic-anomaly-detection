import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from backend.app.models.events import ThreatIncident, RiskLevel
from backend.app.database.repository import AuditRepository

class HoneytokenDetector:
    """
    Genuine honeytoken detector that monitors decoy files (.env.decoy)
    and canary secret strings (VETO_HONEYTOKEN_83921, FAKE_DATABASE_SECRET).
    """

    DECOY_FILES = {
        "/workspace/.env.decoy",
        ".env.decoy",
        "agent/workspace/.env.decoy"
    }

    CANARY_SECRETS = {
        "VETO_HONEYTOKEN_83921": "Decoy Production API Key",
        "FAKE_DATABASE_SECRET": "Decoy DB Master Password",
        "CANARY_KEY_74829103": "Decoy Cloud Storage Credential"
    }

    def __init__(self, repository: Optional[AuditRepository] = None):
        self.repo = repository or AuditRepository()

    def check_resource_access(self, target_resource: str) -> Tuple[bool, Optional[str]]:
        """
        Detects if an operation attempts to read or touch a decoy file.
        """
        for decoy in self.DECOY_FILES:
            if decoy in target_resource or target_resource.endswith(".env.decoy"):
                return True, f"Honeytoken file access attempt: {target_resource}"
        return False, None

    def scan_payload_for_secrets(self, payload: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Scans request parameters or outbound data for known canary tokens.
        Returns: (detected, matched_token, description)
        """
        payload_str = str(payload)
        for token, desc in self.CANARY_SECRETS.items():
            if token in payload_str:
                return True, token, desc
        return False, None, None

    async def create_threat_incident(
        self,
        threat_type: str,
        description: str,
        details: Dict[str, Any]
    ) -> ThreatIncident:
        incident = ThreatIncident(
            id=f"THR-{uuid.uuid4().hex[:10].upper()}",
            timestamp=datetime.now(timezone.utc),
            threat_type=threat_type,
            severity=RiskLevel.CRITICAL,
            description=description,
            details=details,
            blocked=True
        )
        return await self.repo.save_threat(incident)
