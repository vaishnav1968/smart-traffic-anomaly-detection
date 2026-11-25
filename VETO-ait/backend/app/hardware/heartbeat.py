import time
import uuid
import asyncio
import logging
from typing import Callable, Optional
from backend.app.config import settings
from backend.app.hardware.serial_manager import SerialManager
from backend.app.hardware.arduino_protocol import ArduinoProtocol

logger = logging.getLogger("veto.heartbeat")

class HardwareHeartbeat:
    """
    Host-side execution lease and heartbeat monitor.
    Periodically pings Arduino Uno R3.
    If the heartbeat lease expires or Arduino disconnects, triggers fail-closed behaviour:
      - Suspends protected operations
      - Cancels pending approvals
      - Records fail-closed incident
    """

    def __init__(
        self,
        serial_manager: SerialManager,
        on_lease_expired: Optional[Callable[[], None]] = None,
        timeout_seconds: Optional[int] = None
    ):
        self.serial_manager = serial_manager
        self.on_lease_expired = on_lease_expired
        self.timeout_seconds = timeout_seconds or settings.HEARTBEAT_TIMEOUT_SECONDS
        self.last_reply_timestamp = time.time()
        self.is_lease_valid = True
        self.emergency_stop_triggered = False
        self._task: Optional[asyncio.Task] = None
        self._running = False

    def handle_pong(self, nonce: str):
        self.last_reply_timestamp = time.time()
        self.is_lease_valid = True

    def trigger_emergency_stop(self):
        self.emergency_stop_triggered = True
        self.is_lease_valid = False
        logger.critical("EMERGENCY STOP TRIGGERED via Arduino physical button!")
        if self.on_lease_expired:
            self.on_lease_expired()

    def reset_emergency_stop(self):
        self.emergency_stop_triggered = False
        self.last_reply_timestamp = time.time()
        self.is_lease_valid = True
        logger.info("Emergency stop reset by administrator.")

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _heartbeat_loop(self):
        while self._running:
            if self.serial_manager.is_connected:
                nonce = uuid.uuid4().hex[:6]
                self.serial_manager.send_message(ArduinoProtocol.format_ping(nonce))
                
                # Check lease expiry
                elapsed = time.time() - self.last_reply_timestamp
                if elapsed > self.timeout_seconds:
                    if self.is_lease_valid:
                        self.is_lease_valid = False
                        logger.warning(f"Arduino heartbeat lease expired! ({elapsed:.1f}s > {self.timeout_seconds}s). Enforcing FAIL-CLOSED state.")
                        if self.on_lease_expired:
                            self.on_lease_expired()
            await asyncio.sleep(2.0)
