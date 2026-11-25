from urllib.parse import urlparse
from typing import Dict, Any, Tuple
from backend.app.config import settings
from backend.app.security.honeytoken_detector import HoneytokenDetector

class EgressController:
    """
    Host-side egress controller and proxy enforcement.
    Validates outbound destination URLs and scans outbound payloads for exfiltration of honeytoken secrets.
    """

    ALLOWED_HOSTS = {
        "api.weather.gov",
        "httpbin.org",
        "api.github.com",
        "localhost",
        "127.0.0.1"
    }

    BLOCKED_HOSTS = {
        "attacker.com",
        "evil-exfil.xyz",
        "webhook.site",
        "pastebin.com",
        "paste.ee"
    }

    def __init__(self, honeytoken_detector: HoneytokenDetector):
        self.honeytoken_detector = honeytoken_detector

    def inspect_outbound_request(
        self,
        url: str,
        payload: Any
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Inspects an outbound HTTP or network request.
        Returns: (is_permitted, reason, details)
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or url
        except Exception:
            hostname = url

        # 1. Inspect payload for honeytoken secrets (CRITICAL EXFILTRATION ATTEMPT)
        has_token, token, desc = self.honeytoken_detector.scan_payload_for_secrets(payload)
        if has_token:
            return False, f"EGRESS BLOCKED: Honeytoken canary '{token}' ({desc}) detected in outbound payload", {
                "destination": url,
                "violation": "HONEYTOKEN_LEAK",
                "detected_token": token
            }

        # Also inspect URL query params for honeytoken
        has_url_token, url_token, url_desc = self.honeytoken_detector.scan_payload_for_secrets(url)
        if has_url_token:
            return False, f"EGRESS BLOCKED: Honeytoken canary '{url_token}' detected in URL query parameters", {
                "destination": url,
                "violation": "HONEYTOKEN_IN_URL",
                "detected_token": url_token
            }

        # 2. Check blocked / malicious hosts
        if any(bad in hostname.lower() for bad in self.BLOCKED_HOSTS):
            return False, f"EGRESS BLOCKED: Destination '{hostname}' is on the hostile endpoint blacklist", {
                "destination": url,
                "violation": "PROHIBITED_HOST"
            }

        # 3. Check allowed hosts whitelist (strict mode)
        if not any(hostname.lower() == allowed or hostname.lower().endswith("." + allowed) for allowed in self.ALLOWED_HOSTS):
            return False, f"EGRESS BLOCKED: Destination '{hostname}' is not in the allowed destinations whitelist", {
                "destination": url,
                "violation": "UNAPPROVED_EGRESS_DESTINATION"
            }

        return True, "Egress request authorized to whitelisted endpoint without secrets", {
            "destination": url,
            "status": "ALLOWED"
        }
