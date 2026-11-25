import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    VETO_ENV: str = "development"
    VETO_HOST: str = "0.0.0.0"
    VETO_PORT: int = 8000
    VETO_SECRET_KEY: str = "veto_super_secret_local_key_change_in_production"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_PATH: str = "veto_audit.db"
    POLICIES_FILE: str = "configs/policies.yaml"
    MCP_TOOLS_FILE: str = "configs/mcp_tools.json"
    WORKSPACE_DIR: str = "agent/workspace"
    
    # LLM Settings
    GROK_API_KEY: str = ""
    MODEL_NAME: str = "grok-beta"
    API_BASE_URL: str = "https://api.x.ai/v1"
    
    # Arduino Hardware Settings
    ARDUINO_PORT: str = "COM3"
    ARDUINO_BAUD: int = 115200
    ARDUINO_SIMULATION_MODE: bool = False
    
    # Safety & timeouts
    APPROVAL_TIMEOUT_SECONDS: int = 60
    HEARTBEAT_TIMEOUT_SECONDS: int = 5
    FAIL_CLOSED: bool = True

settings = Settings()
