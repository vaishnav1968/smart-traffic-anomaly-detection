# VETO Threat Model & Security Limitations

## 1. Threat Model & Protected Assets

### Primary Protected Assets
1. **Host Integrity:** Preventing AI agents from modifying host files, executing unauthorized shell commands, or breaking out of execution sandboxes.
2. **Sensitive Configuration & Code:** Preventing unauthorized deletion, tampering, or overwriting of production configs (`system_config.json`, `.env`).
3. **Decoy Credentials & Secrets:** Detecting attempts to harvest credentials via prompt injections or supply chain attacks.
4. **Data Exfiltration:** Intercepting outbound network requests containing sensitive tokens.

---

## 2. Threat Scenarios & Mitigations

| Threat | Attack Vector | VETO Mitigation Mechanism | Result |
| :--- | :--- | :--- | :--- |
| **Indirect Prompt Injection** | Malicious text in repository (`README_task.md`) instructs agent to read secret files. | Honeytoken detector traps `.env.decoy` access. | **AUTO-VETO** (Blocked + High-Severity Incident) |
| **Credential Exfiltration** | Agent attempts HTTP POST with stolen API token to attacker server. | Egress Controller inspects payload and URL for known canary tokens. | **AUTO-VETO** (Outbound traffic blocked) |
| **MCP Tool Tampering** | Compromised tool provider adds unauthorized capabilities (e.g. `system:arbitrary_exec`). | SHA-256 canonical metadata fingerprint verification. | **AUTO-VETO** (Execution paused + alert) |
| **Destructive Command Execution** | Agent attempts `rm -rf /` or reverse shell `curl ... \| bash`. | Deterministic pattern matching & risk classification. | **AUTO-VETO** (Blocked immediately) |
| **Accidental or Malicious Deletion** | Agent attempts deletion of critical configuration file. | Policy rule `RULE-REVIEW-FILE-DELETION`. | **HUMAN REVIEW** (Requires physical button press) |
| **Path Traversal / Sandbox Breakout** | Agent requests `../../etc/shadow` or `C:\Windows`. | Path traversal regex + runtime path containment validation. | **AUTO-VETO** (Boundary violation blocked) |
| **Hardware Link Interruption** | USB cable disconnected or physical emergency stop button triggered. | Execution lease heartbeat monitor fails closed. | **FAIL-CLOSED** (Pending actions cancelled) |

---

## 3. Explicit Security Boundaries & Assumptions

### A. Arduino Uno R3 Security Limitations
> [!IMPORTANT]
> The Arduino Uno R3 (ATmega328P) does **NOT** feature a hardware Secure Element, cryptographic keystore, or cryptographic USB hardware authentication.
- **Threat Boundary:** The Arduino is utilized as a **physical human control and visual verification interface**, **not** as an authoritative cryptographic hardware root-of-trust.
- **Enforcement Authority:** Host-side VETO services enforce all decisions, validate nonces, check action hashes, and handle lease timeouts.
- **Physical USB Channel:** The serial link over USB is unauthenticated plain-text. If an attacker gains root code execution on the host machine, they could simulate serial bytes. Therefore, the agent container is strictly isolated from accessing host `/dev/tty*` serial devices.

### B. Docker Sandbox Boundaries
- The AI agent container runs with `no-new-privileges:true`, non-root user `agentuser`, `cap_drop: ALL`, and no access to `/var/run/docker.sock`.
- It does **not** protect against kernel 0-day privilege escalations if the container runtime itself is vulnerable.

### C. Honeytoken Limitations
> [!NOTE]
> Honeytoken monitoring and egress inspection detect plaintext or lightly encoded tokens matching known canary signatures. They do not claim detection of steganographic, heavily encrypted, or covert side-channel exfiltration channels.

### D. Hash-Chained Audit Ledger
> [!NOTE]
> Hash chaining provides tamper-evidence against database record tampering under standard threat models. An adversary with full host root access who truncates the entire database and re-computes an entire synthetic chain from scratch would require external timestamping or ledger notarization to detect.
