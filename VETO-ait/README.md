# VETO: Zero-Trust Runtime Security for Autonomous AI Agents

> *"Intelligence should never automatically grant authority."*

**VETO** is a runtime security enforcement platform that intercepts autonomous AI agent operations, evaluates them against deterministic policies, and permits, blocks, or requests human approval before any protected action executes.

---

## 1. Core Principles & Decisions

Every intercepted operation receives one of three deterministic decisions prior to execution:
1. **ALLOW:** Automatically permit authorized, low-risk operations (e.g. reading permitted project files).
2. **REVIEW:** Pause sensitive or destructive operations and request human authorization via **Arduino Uno R3** physical buttons or the **Web Approval Center**.
3. **VETO:** Immediately terminate prohibited operations (e.g. honeytoken access, unauthorized network egress, path traversal, prohibited shell commands).

The security policy engine is **100% deterministic** and **never relies on an LLM to make security decisions**.

---

## 2. System Architecture

```
AI Agent (Docker / Sandbox Jail)
    |
    v
VETO Interception Layer (POST /api/intercept)
    |
    +---- MCP Integrity Verification (SHA-256 canonical fingerprinting)
    +---- Honeytoken Decoy File Monitor (.env.decoy)
    +---- Network Egress Controller & Secret Scanner
    |
    v
Deterministic Security Policy Engine (YAML rules, fail-closed)
    |
    +---- AUTO-ALLOW  ---> Controlled Execution Sandbox
    |
    +---- HUMAN REVIEW ---> Arduino Uno R3 OLED & Web Approval Center
    |                          |
    |                          +--> APPROVED ---> Controlled Execution
    |                          +--> REJECTED ---> Blocked & Preserved
    |
    +---- AUTO-VETO   ---> Blocked Immediately & Forensic Alert
    |
    v
Tamper-Evident SHA-256 Hash-Chained Audit Ledger (SQLite WAL)
    |
    v
Web Operations Center (React + TypeScript + Tailwind CSS @ localhost:8000)
```

---

## 3. Security Subsystems

### 3.1 Controlled Execution Sandbox
- Isolates agent actions inside a restricted Docker container (`agentuser`, no root, `cap_drop: ALL`, no Docker socket access) or an isolated local workspace jail (`agent/workspace/`).
- Strictly enforces canonical path containment to prevent path traversal (`../`).

### 3.2 Honeytoken Detection & Exfiltration Prevention
- Places decoy credential files (`.env.decoy`) with canary tokens (`VETO_HONEYTOKEN_83921`).
- Monitors read/touch access to decoy resources.
- Egress controller scans outbound payloads and blocks attempts to transmit honeytokens to external endpoints.

### 3.3 MCP Tool Integrity Verification
- Computes SHA-256 canonical fingerprints over tool metadata (name, description, version, input schema, capabilities).
- Automatically detects unauthorized capabilities (e.g. `system:arbitrary_exec`) and blocks execution on mismatch.

### 3.4 Physical Human-Control Interface (Arduino Uno R3)
- **OLED Display (SSD1306 I2C):** Displays pending approval ID, operation name, and target resource.
- **Physical Buttons:** Momentary `APPROVE` and `REJECT` buttons, plus an `EMERGENCY STOP` switch.
- **RGB LED:** Green (Nominal), Amber (Review Pending), Red (Blocked / E-Stop).
- **Fail-Closed Heartbeat:** If the Arduino disconnects or heartbeat lease expires, all pending operations are cancelled and execution is suspended.
- **Disconnected Hardware Mode:** When testing without physical hardware, VETO automatically switches to a clearly labelled simulation mode with full Web UI controls.

### 3.5 Tamper-Evident Hash-Chained Audit Ledger
- Cryptographically chains every security event using SHA-256.
- Detects any database modification or record alteration with a single click.

---

## 4. Quick Start & Setup

### Option A: Local Installation (Windows PowerShell)

```powershell
# 1. Run Setup (Creates .venv, installs dependencies, builds frontend)
.\scripts\setup.ps1

# 2. Run automated test suite
$env:PYTHONPATH="."
.\.venv\Scripts\pytest.exe -v

# 3. Launch VETO Platform
.\scripts\run.ps1
```

### Option B: Local Installation (Linux / macOS Bash)

```bash
# 1. Run Setup
chmod +x scripts/*.sh
./scripts/setup.sh

# 2. Run automated test suite
PYTHONPATH="." ./.venv/bin/pytest -v

# 3. Launch VETO Platform
./scripts/run.sh
```

### Option C: Docker Deployment

```bash
docker compose up --build
```

Access the Web Dashboard at: **`http://localhost:8000`**

---

## 5. Hardware Setup (Arduino Uno R3)

### Wiring Pinout:
- **SSD1306 OLED (I2C):** `VCC` -> 5V, `GND` -> GND, `SDA` -> A4, `SCL` -> A5
- **APPROVE Button:** Digital Pin 2 (`INPUT_PULLUP` to GND)
- **REJECT Button:** Digital Pin 3 (`INPUT_PULLUP` to GND)
- **EMERGENCY STOP Button:** Digital Pin 4 (`INPUT_PULLUP` to GND)
- **RGB LED (Common-Cathode with 220 $\Omega$ resistors):** Red -> Pin 9, Green -> Pin 10, Blue -> Pin 11

### Flashing Firmware:
Upload `firmware/veto_controller/veto_controller.ino` via the Arduino IDE with libraries `Adafruit SSD1306` and `Adafruit GFX`.

Detailed schematics and instructions: [docs/hardware_setup.md](file:///c:/Users/vaish/VETO-ait/docs/hardware_setup.md)

---

## 6. Three-Minute Demonstration Scenarios

VETO includes three one-click reproducible demonstration scenarios accessible from the **Demo Scenarios** tab:

1. **DEMO 1 — Prompt Injection & Honeytoken Exfiltration:**
   - Agent is misled by a repository README prompt injection to access `.env.decoy`.
   - VETO traps the access (**AUTO-VETO**).
   - Agent attempts to transmit canary token to `http://attacker.com/collect`.
   - Egress controller blocks the outbound transmission (**BLOCKED**).

2. **DEMO 2 — MCP Tool Tampering:**
   - Modifies approved tool definition of `read_file` to inject unauthorized capability `system:arbitrary_exec`.
   - VETO detects SHA-256 fingerprint mismatch and halts execution (**BLOCKED — MCP INTEGRITY VIOLATION**).

3. **DEMO 3 — Physical Approval & Rejection:**
   - Agent attempts deletion of protected file `system_config.json`.
   - VETO intercepts and broadcasts review request to Arduino OLED and Web Approval Center.
   - User presses **REJECT**.
   - VETO rejects the action and proves `system_config.json` remains preserved on disk (**REJECTED**).

Step-by-step guide: [docs/demo_guide.md](file:///c:/Users/vaish/VETO-ait/docs/demo_guide.md)

---

## 7. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | System health, Arduino port status, sandbox mode, and summary metrics |
| `POST` | `/api/intercept` | Core interception gateway for agent tool calls |
| `GET` | `/api/events` | List recorded security events from audit log |
| `GET` | `/api/events/{id}` | Detailed forensic dossier for a specific event |
| `GET` | `/api/approvals` | List pending and historical human review requests |
| `POST` | `/api/approvals/{id}/approve` | Authorize pending action (Web Dashboard) |
| `POST` | `/api/approvals/{id}/reject` | Reject pending action (Web Dashboard) |
| `POST` | `/api/emergency-stop` | Trigger emergency stop across all agent execution |
| `POST` | `/api/emergency-stop/reset` | Reset emergency stop state |
| `GET` | `/api/threats` | List forensic threat incidents |
| `GET` | `/api/mcp/integrity` | Catalog of registered MCP tools and SHA-256 fingerprints |
| `POST` | `/api/mcp/tamper` | Demonstration helper to simulate tool tampering |
| `POST` | `/api/mcp/approve-fingerprint` | Re-approves current fingerprint as baseline |
| `GET` | `/api/audit/verify` | Runs complete SHA-256 cryptographic hash-chain verification |
| `POST` | `/api/demo/{scenario}/run` | Executes one-click reproducible demonstration scenario |
| `WS` | `/ws` | Real-time WebSocket connection for live telemetry |

---

## 8. Documentation Index

- [Architecture Specification](file:///c:/Users/vaish/VETO-ait/docs/architecture.md)
- [Threat Model & Security Limitations](file:///c:/Users/vaish/VETO-ait/docs/threat_model.md)
- [Hardware Wiring & Firmware Setup](file:///c:/Users/vaish/VETO-ait/docs/hardware_setup.md)
- [3-Minute Demonstration Guide](file:///c:/Users/vaish/VETO-ait/docs/demo_guide.md)
- [Development Feature Manifest](file:///c:/Users/vaish/VETO-ait/DEVELOPMENT.md)
