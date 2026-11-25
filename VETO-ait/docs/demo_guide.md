# VETO 3-Minute Demonstration Guide

This guide provides step-by-step instructions for demonstrating VETO to evaluators and stakeholders.

---

## Prerequisites
1. Backend running: `http://localhost:8000`
2. Frontend Dashboard open: `http://localhost:8000` (or `http://localhost:5173`)
3. Optional: Arduino Uno R3 plugged into USB (COM3) with OLED and buttons wired. (If no Arduino is present, VETO operates in clearly labelled Simulation Mode with full Web UI verification).

---

## 3-Minute Demonstration Timeline

```
+-------------------------------------------------------------------------------+
|  TIME   | SECTION                     | ACTION                                |
+-------------------------------------------------------------------------------+
| 00:00   | System Status & Zero-Trust  | Show Dashboard Overview & Indicators  |
| 00:45   | DEMO 1: Prompt Injection    | Trigger Honeytoken & Egress Block     |
| 01:30   | DEMO 2: MCP Tool Tampering  | Simulate Metadata Tampering & Pause   |
| 02:15   | DEMO 3: Physical Control    | Trigger Deletion -> REJECT on Arduino |
| 02:50   | Audit Ledger Verification   | Cryptographic SHA-256 Chain Verify    |
+-------------------------------------------------------------------------------+
```

---

## Walkthrough Steps

### Step 1: System Overview (00:00 - 00:45)
1. Open the VETO Dashboard.
2. Highlight:
   - **Enforcement Principle:** "Intelligence should never automatically grant authority."
   - **Sandbox Status:** Verified boundary check active.
   - **Arduino Status:** Shows connected COM port (or clearly labelled Disconnected Simulation Mode).
   - **Policy Engine:** Deterministic rule evaluation (0% LLM hallucination in security decisions).

---

### Step 2: DEMO 1 — Prompt Injection & Honeytoken Exfiltration (00:45 - 01:30)
1. Navigate to **Demo Scenarios** in the sidebar.
2. Click **Run Demo 1**.
3. Observe live execution steps:
   - **Step 1:** Reading `README_task.md` is **ALLOWED** (routine project file).
   - **Step 2:** Misled by README instruction, agent attempts to read `.env.decoy`. VETO detects honeytoken access: **BLOCKED (VETO)**.
   - **Step 3:** Agent attempts to transmit token to `http://attacker.com/collect`. Egress Controller detects canary secret: **BLOCKED (VETO)**.
4. Navigate to **Threat Detection** page to show the recorded forensic incident dossier.

---

### Step 3: DEMO 2 — MCP Tool Tampering (01:30 - 02:15)
1. Navigate to **MCP Integrity** page.
2. Show that `read_file` is initially **VERIFIED** with approved SHA-256 fingerprint.
3. Click **Simulate Tampering** on `read_file`.
4. Observe:
   - Status instantly flips to **TAMPERED (Red pulse)**.
   - An unauthorized capability `system:arbitrary_exec` was injected into the tool schema.
5. In **Demo Scenarios**, click **Run Demo 2**:
   - The agent attempts to call `read_file`.
   - VETO intercepts the tool call, detects the fingerprint mismatch, and halts execution: **BLOCKED — MCP INTEGRITY VIOLATION**.

---

### Step 4: DEMO 3 — Physical Approval and Rejection (02:15 - 02:50)
1. In **Demo Scenarios**, run **Demo 3** (or manually dispatch `delete_file` on `system_config.json` via the Interactive Interceptor on the Overview page).
2. Observe:
   - Policy Engine marks deletion as **HUMAN REVIEW**.
   - Arduino Uno R3 OLED updates: `REQ: APR-XXXX | OP: DELETE | TGT: system_config.json`.
   - Arduino RGB LED turns **Amber / Yellow**.
   - Web Dashboard **Approval Center** displays the pending approval card with action hash.
3. Press **REJECT** button on the Arduino (or click REJECT in the Web Dashboard).
4. Observe:
   - Arduino OLED displays `REJECTED`, LED pulses **Red**.
   - Confirmation displayed: `system_config.json` was **NOT deleted** and remains secured on disk.

---

### Step 5: Cryptographic Audit Ledger Verification (02:50 - 03:00)
1. Navigate to **Audit Trail** page.
2. Show the continuous SHA-256 hash chain linked to every event.
3. Click **Verify Complete Hash Chain**.
4. Observe verification outcome: `LEDGER INTEGRITY VERIFIED (Events Checked: X. Chain integrity 100% valid)`.
