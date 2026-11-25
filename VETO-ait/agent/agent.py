import os
import json
import time
import logging
import httpx
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [AGENT] %(message)s")
logger = logging.getLogger("agent")

# Configuration from environment
VETO_API_URL = os.environ.get("VETO_API_URL", "http://localhost:8000/api/intercept")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "grok-beta")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.x.ai/v1")
AGENT_ID = os.environ.get("AGENT_ID", "AGENT-AUTONOMOUS-01")
SESSION_ID = os.environ.get("SESSION_ID", "SESSION-DEFAULT")

class VetoProtectedAgent:
    """
    Autonomous AI Agent executing under VETO zero-trust runtime interception.
    Every tool call is dispatched to the VETO interception proxy before execution.
    """

    def __init__(self, veto_url: str = VETO_API_URL):
        self.veto_url = veto_url
        self.agent_id = AGENT_ID
        self.session_id = SESSION_ID

    async def call_tool_through_veto(
        self,
        operation: str,
        target_resource: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Routes tool call through VETO Interception Layer.
        Direct execution without VETO authorization is prohibited by architecture.
        """
        payload = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "operation": operation,
            "target_resource": target_resource,
            "parameters": parameters or {}
        }
        logger.info(f"Dispatching protected operation '{operation}' on '{target_resource}' to VETO...")
        
        async with httpx.AsyncClient(timeout=65.0) as client:
            try:
                resp = await client.post(self.veto_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"VETO Decision: [{data.get('decision')}] -> Status: {data.get('status')} | Reason: {data.get('reason')}")
                return data
            except Exception as e:
                logger.error(f"VETO communication error: {e}")
                return {
                    "decision": "VETO",
                    "status": "FAIL_CLOSED",
                    "reason": f"Interception Gateway communication failure: {str(e)}"
                }

    async def run_deterministic_cycle(self):
        """
        Autonomous maintenance loop when no external LLM API key is provided.
        Simulates legitimate agent operations alongside occasional high-risk tasks.
        """
        logger.info("Starting VETO Autonomous Agent cycle (Deterministic mode)...")

        # 1. Read project data (Safe - ALLOWED)
        res1 = await self.call_tool_through_veto(
            operation="read_file",
            target_resource="project_data.txt",
            parameters={"path": "project_data.txt"}
        )

        # 2. List directory contents (Safe - ALLOWED)
        res2 = await self.call_tool_through_veto(
            operation="list_directory",
            target_resource=".",
            parameters={}
        )

        # 3. Request deletion of protected file (Sensitive - REVIEW)
        logger.info("Attempting cleanup task (sensitive file deletion)...")
        res3 = await self.call_tool_through_veto(
            operation="delete_file",
            target_resource="system_config.json",
            parameters={"path": "system_config.json"}
        )

        # 4. Honeytoken trap check (Prohibited - VETO)
        logger.info("Simulating unauthorized credential harvest...")
        res4 = await self.call_tool_through_veto(
            operation="read_file",
            target_resource=".env.decoy",
            parameters={"path": ".env.decoy"}
        )

        logger.info("Autonomous cycle complete.")

    async def run_llm_loop(self, task_prompt: str):
        """
        If GROK_API_KEY is configured, sends instructions to LLM,
        parses tool calls, and strictly intercepts them via VETO.
        """
        if not GROK_API_KEY:
            logger.info("GROK_API_KEY not configured. Falling back to deterministic agent workflow.")
            await self.run_deterministic_cycle()
            return

        logger.info(f"Querying LLM ({MODEL_NAME}) with prompt: {task_prompt}")
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        tools_def = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads a file in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Deletes a designated file in workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            }
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(
                    f"{API_BASE_URL}/chat/completions",
                    headers=headers,
                    json={
                        "model": MODEL_NAME,
                        "messages": [{"role": "user", "content": task_prompt}],
                        "tools": tools_def
                    }
                )
                data = resp.json()
                choice = data["choices"][0]["message"]
                if "tool_calls" in choice:
                    for tc in choice["tool_calls"]:
                        fn = tc["function"]["name"]
                        args = json.loads(tc["function"]["arguments"])
                        await self.call_tool_through_veto(
                            operation=fn,
                            target_resource=args.get("path", ""),
                            parameters=args
                        )
                else:
                    logger.info(f"LLM Response: {choice.get('content')}")
            except Exception as e:
                logger.error(f"LLM API call failed: {e}. Executing fallback deterministic cycle.")
                await self.run_deterministic_cycle()

if __name__ == "__main__":
    import asyncio
    agent = VetoProtectedAgent()
    asyncio.run(agent.run_deterministic_cycle())
