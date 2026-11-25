class ArduinoProtocol:
    """
    Message protocol specification for Arduino Uno R3 communication.
    
    Host -> Arduino:
      STATUS:<text>                (e.g., STATUS:SYSTEM NORMAL)
      PENDING:<id>:<op>:<target>   (e.g., PENDING:APR-9812:DELETE:system_config.json)
      DECISION:<id>:<decision>     (e.g., DECISION:APR-9812:APPROVED)
      PING:<nonce>                 (Heartbeat keepalive query)
      ESTOP_RESET                  (Clears emergency-stop state on Arduino)
    
    Arduino -> Host:
      READY                        (Sent when Arduino boots or resets)
      APPROVE:<id>                 (Physical APPROVE button pressed for active ID)
      REJECT:<id>                  (Physical REJECT button pressed for active ID)
      ESTOP                        (Physical EMERGENCY-STOP button triggered)
      PONG:<nonce>                 (Heartbeat keepalive response)
      HEARTBEAT                    (Periodic status ping from Arduino)
    """

    @staticmethod
    def format_status(status_text: str) -> str:
        return f"STATUS:{status_text[:20]}\n"

    @staticmethod
    def format_pending(approval_id: str, operation: str, target: str) -> str:
        # Arduino OLED line width is limited (approx 16-20 chars)
        clean_op = operation[:8].upper()
        clean_target = target.split("/")[-1][:12]
        return f"PENDING:{approval_id}:{clean_op}:{clean_target}\n"

    @staticmethod
    def format_decision(approval_id: str, decision: str) -> str:
        return f"DECISION:{approval_id}:{decision.upper()}\n"

    @staticmethod
    def format_ping(nonce: str) -> str:
        return f"PING:{nonce}\n"

    @staticmethod
    def parse_message(raw_line: str):
        line = raw_line.strip()
        if not line:
            return None, None

        if line == "READY":
            return "READY", {}
        elif line == "ESTOP":
            return "ESTOP", {}
        elif line == "HEARTBEAT":
            return "HEARTBEAT", {}
        elif line.startswith("APPROVE:"):
            parts = line.split(":", 1)
            return "APPROVE", {"approval_id": parts[1].strip()}
        elif line.startswith("REJECT:"):
            parts = line.split(":", 1)
            return "REJECT", {"approval_id": parts[1].strip()}
        elif line.startswith("PONG:"):
            parts = line.split(":", 1)
            return "PONG", {"nonce": parts[1].strip()}
        else:
            return "UNKNOWN", {"raw": line}
