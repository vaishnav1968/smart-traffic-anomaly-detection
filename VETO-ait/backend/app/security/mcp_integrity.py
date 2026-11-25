import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from backend.app.config import settings

class MCPIntegrityVerifier:
    """
    SHA-256 tool integrity verification.
    Canonicalises MCP tool definitions before hashing, including:
    - Tool name
    - Description
    - Version
    - Input schema
    - Capabilities

    Detects metadata changes, unexpected capabilities, and triggers execution pauses.
    """

    def __init__(self, mcp_config_path: Optional[str] = None):
        self.config_path = mcp_config_path or settings.MCP_TOOLS_FILE
        self._tools: Dict[str, Dict[str, Any]] = {}
        self.load_tools()

    def canonicalise_tool_definition(self, tool_def: Dict[str, Any]) -> str:
        """
        Extracts canonical fields and generates deterministic JSON string.
        """
        canonical_dict = {
            "name": tool_def.get("name", "").strip(),
            "description": tool_def.get("description", "").strip(),
            "version": tool_def.get("version", "1.0.0"),
            "input_schema": tool_def.get("input_schema", {}),
            "capabilities": sorted(tool_def.get("capabilities", []))
        }
        return json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"))

    def compute_fingerprint(self, tool_def: Dict[str, Any]) -> str:
        canonical_str = self.canonicalise_tool_definition(tool_def)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def load_tools(self) -> Dict[str, Dict[str, Any]]:
        p = Path(self.config_path)
        if not p.is_absolute():
            p = settings.BASE_DIR / p
        
        if not p.exists():
            return {}

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._tools = {}
        for tool in data.get("tools", []):
            name = tool["name"]
            # Recalculate current fingerprint
            current_fp = self.compute_fingerprint(tool)
            tool["current_fingerprint"] = current_fp
            
            # If approved_fingerprint matches
            if tool.get("approved_fingerprint") == current_fp:
                tool["status"] = "VERIFIED"
            else:
                tool["status"] = "TAMPERED"

            tool["last_verified"] = datetime.now(timezone.utc).isoformat()
            self._tools[name] = tool

        return self._tools

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        return self._tools.get(tool_name)

    def get_all_tools(self) -> List[Dict[str, Any]]:
        return list(self._tools.values())

    def verify_tool_integrity(self, tool_name: str) -> Tuple[bool, str, Dict[str, Any]]:
        tool = self.get_tool(tool_name)
        if not tool:
            return False, f"Unknown tool: '{tool_name}' is not registered in MCP catalog", {}

        current_fp = self.compute_fingerprint(tool)
        approved_fp = tool.get("approved_fingerprint", "")

        is_valid = (current_fp == approved_fp)
        details = {
            "name": tool_name,
            "approved_fingerprint": approved_fp,
            "current_fingerprint": current_fp,
            "status": "VERIFIED" if is_valid else "TAMPERED",
            "last_verified": datetime.now(timezone.utc).isoformat()
        }

        if is_valid:
            tool["status"] = "VERIFIED"
            return True, f"MCP Tool '{tool_name}' fingerprint verified successfully", details
        else:
            tool["status"] = "TAMPERED"
            return False, f"MCP INTEGRITY VIOLATION: Tool '{tool_name}' fingerprint mismatch! Expected {approved_fp[:16]}..., got {current_fp[:16]}...", details

    def simulate_tampering(self, tool_name: str) -> Dict[str, Any]:
        """
        Demonstration helper: Modifies tool definition by adding an unexpected destructive capability.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")

        # Inject unexpected destructive capability
        if "capabilities" not in tool:
            tool["capabilities"] = []
        if "system:arbitrary_exec" not in tool["capabilities"]:
            tool["capabilities"].append("system:arbitrary_exec")
            tool["description"] = tool["description"] + " [MODIFIED: unauthorized background telemetry]"

        current_fp = self.compute_fingerprint(tool)
        tool["current_fingerprint"] = current_fp
        tool["status"] = "TAMPERED"
        tool["last_verified"] = datetime.now(timezone.utc).isoformat()
        return tool

    def approve_tool_fingerprint(self, tool_name: str) -> Dict[str, Any]:
        """
        Re-approves current fingerprint as new baseline.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")

        current_fp = self.compute_fingerprint(tool)
        tool["approved_fingerprint"] = current_fp
        tool["status"] = "VERIFIED"
        tool["last_verified"] = datetime.now(timezone.utc).isoformat()
        return tool
