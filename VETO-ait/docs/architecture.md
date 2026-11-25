# VETO System Architecture

## 1. Architectural Overview

**VETO** is a zero-trust runtime security layer designed to enforce strict security boundaries on autonomous AI agents prior to operation execution.

```
                  +----------------------------------------+
                  |         Autonomous AI Agent            |
                  |   (Running in Docker / Local Jail)     |
                  +----------------------------------------+
                                      |
                                      v
                 [ VETO HTTP / MCP Interception Gateway ]
                                      |
                                      v
                  +----------------------------------------+
                  |         Security Pre-Filters           |
                  |  - MCP Tool SHA-256 Verification       |
                  |  - Honeytoken Decoy File Monitor       |
                  |  - Egress Controller & Secret Scanner  |
                  +----------------------------------------+
                                      |
                                      v
                  +----------------------------------------+
                  |        Deterministic Policy Engine     |
                  |  - Priority 1-9:   AUTO-VETO           |
                  |  - Priority 10-19: HUMAN REVIEW        |
                  |  - Priority 20-29: AUTO-ALLOW          |
                  |  - Fail-Closed:    Enforced            |
                  +----------------------------------------+
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
          v                           v                           v
     [ ALLOW ]                   [ REVIEW ]                    [ VETO ]
          |                           |                           |
          |               +-----------------------+               |
          |               | Dual Approval Engine  |               |
          |               | - Arduino Uno R3 OLED |               |
          |               | - Web Approval Center |               |
          |               +-----------------------+               |
          |                  /                 \                  |
          |           [ APPROVED ]         [ REJECTED ]           |
          |                 |                   |                 |
          v                 v                   |                 |
     +---------------------------+              v                 v
     |   Controlled Execution    |     +-------------------------------+
     | - Filesystem Jail Check   |     |      Operation Blocked        |
     | - Non-root sandbox exec   |     | - Security Incident Logged    |
     +---------------------------+     +-------------------------------+
                   \                                   /
                    \                                 /
                     v                               v
         +-------------------------------------------------------+
         |         Tamper-Evident SHA-256 Hash Chained Ledger    |
         |         (Previous Hash -> Current Event Hash)         |
         +-------------------------------------------------------+
                                     |
                                     v
         +-------------------------------------------------------+
         |     React + TypeScript Security Operations Center     |
         |     (Real-Time WebSocket Feed @ localhost:8000)       |
         +-------------------------------------------------------+
```

---

## 2. Core Architectural Components

### 2.1 VETO Interception Layer (`backend/app/security/interception_proxy.py`)
All tool calls and operations requested by an agent must pass through the HTTP/MCP interception endpoint (`POST /api/intercept`). The proxy captures:
- Operation type (e.g. `read_file`, `write_file`, `delete_file`, `http_request`, `mcp_tool_call`)
- Target resource (relative or absolute path, URL, host, or command string)
- Execution arguments / parameters
- Agent identity (`agent_id`)
- Session context (`session_id`)

Execution is completely suspended until VETO finishes evaluation.

### 2.2 Deterministic Security Policy Engine (`backend/app/core/policy_engine.py`)
Evaluates operations against YAML-defined rules without invoking LLMs:
- **Priority 1-9 (AUTO-VETO):** Immediately terminates prohibited operations (honeytoken reads, payload secrets, destructive breakouts like `rm -rf /`, path traversals `../`, blacklisted external hosts).
- **Priority 10-19 (HUMAN REVIEW):** Pauses execution for sensitive operations (file deletions, modifying `.env` or system configurations, executing arbitrary shell commands).
- **Priority 20-29 (AUTO-ALLOW):** Permits routine low-risk operations (reading verified workspace files, directory listings, verified read-only MCP tools).
- **Fail-Closed Principle:** Any exception, syntax error, or unhandled rule state forces an immediate `VETO` with `RiskLevel.CRITICAL`.

### 2.3 Dual Human-Control Interface & Approval Manager (`backend/app/core/approval_manager.py`)
When an operation requires human review:
1. Generates an approval record bound to:
   $$\text{Action Hash} = \text{SHA256}(\text{session\_id} \parallel \text{operation} \parallel \text{target\_resource} \parallel \text{canonical\_params})$$
2. Broadcasts the pending operation to the **Arduino Uno R3** physical OLED display and to the **Web Approval Center**.
3. Physical buttons or Web buttons can authorize or reject the request. Resolving on either interface immediately invalidates the other.
4. Timed approvals fail closed upon timeout (default 60 seconds).

### 2.4 Arduino Hardware Controller (`firmware/veto_controller/veto_controller.ino`)
- **Microcontroller:** Arduino Uno R3 (ATmega328P).
- **Display:** 0.96" SSD1306 OLED (I2C address `0x3C`, SDA to A4, SCL to A5).
- **Buttons:** APPROVE (D2), REJECT (D3), EMERGENCY STOP (D4).
- **Status LED:** RGB LED (D9, D10, D11) with series resistors ($220\ \Omega$).
- **Communication:** Structured serial protocol over USB at 115200 baud.
- **Heartbeat Lease:** Host-side heartbeat ping query. If Arduino disconnects or fails heartbeat within lease timeout, protected execution is suspended.

### 2.5 Tamper-Evident Hash-Chained Audit Ledger (`backend/app/security/audit_logger.py`)
Every security event is appended to a cryptographic hash chain:
$$H_0 = 0^{64}$$
$$H_i = \text{SHA256}(H_{i-1} \parallel \text{CanonicalJSON}(\text{Event}_i))$$
Any modification or truncation of past records causes hash verification to fail immediately.
