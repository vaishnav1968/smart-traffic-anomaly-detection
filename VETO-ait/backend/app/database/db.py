import aiosqlite
from pathlib import Path
from backend.app.config import settings

def get_db_path() -> Path:
    db_p = Path(settings.DATABASE_PATH)
    if not db_p.is_absolute():
        db_p = settings.BASE_DIR / db_p
    db_p.parent.mkdir(parents=True, exist_ok=True)
    return db_p

async def init_db():
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        
        # Security events with hash chaining
        await db.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                target_resource TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,
                policy_reason TEXT NOT NULL,
                execution_outcome TEXT NOT NULL,
                parameters TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL
            );
        """)

        # Approvals table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                target_resource TEXT NOT NULL,
                action_hash TEXT NOT NULL,
                parameters TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status TEXT NOT NULL,
                resolved_by TEXT,
                resolved_at TEXT
            );
        """)

        # Threat incidents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS threat_incidents (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT NOT NULL,
                blocked INTEGER NOT NULL
            );
        """)

        # MCP tools registry
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mcp_tools (
                name TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                version TEXT NOT NULL,
                input_schema TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                approved_fingerprint TEXT NOT NULL,
                current_fingerprint TEXT NOT NULL,
                status TEXT NOT NULL,
                last_verified TEXT NOT NULL
            );
        """)

        await db.commit()
