import asyncio
import logging
import serial
import serial.tools.list_ports
from typing import Optional, Callable, Dict, Any
from backend.app.config import settings
from backend.app.hardware.arduino_protocol import ArduinoProtocol

logger = logging.getLogger("veto.hardware")

class SerialManager:
    """
    Manages USB serial communications with Arduino Uno R3.
    Provides fail-closed protection, connection health monitoring,
    and automatic reconnection.
    
    If no physical Arduino is connected, operates in clearly labelled
    'DISCONNECTED / SIMULATION' mode to prevent stalling.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        on_message_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        self.port = port or settings.ARDUINO_PORT
        self.baudrate = baudrate or settings.ARDUINO_BAUD
        self.callback = on_message_callback
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_simulation = settings.ARDUINO_SIMULATION_MODE
        self._running = False
        self._read_task: Optional[asyncio.Task] = None
        self.last_heartbeat_time = 0.0

    def get_status(self) -> Dict[str, Any]:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return {
            "connected": self.is_connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "simulation_mode": self.is_simulation,
            "available_ports": ports,
            "status_label": "PHYSICAL_HARDWARE_CONNECTED" if self.is_connected else ("DISCONNECTED_SIMULATION_MODE" if self.is_simulation else "HARDWARE_DISCONNECTED")
        }

    async def start(self):
        self._running = True
        await self._connect()
        self._read_task = asyncio.create_task(self._read_loop())

    async def stop(self):
        self._running = False
        if self._read_task:
            self._read_task.cancel()
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.is_connected = False

    async def _connect(self):
        try:
            # Check if port exists in available ports
            available = [p.device for p in serial.tools.list_ports.comports()]
            if self.port not in available:
                logger.warning(f"Arduino port {self.port} not found among {available}. Running in DISCONNECTED mode.")
                self.is_connected = False
                return

            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1
            )
            self.is_connected = True
            logger.info(f"Connected to Arduino Uno on {self.port} at {self.baudrate} baud.")
        except Exception as e:
            logger.warning(f"Could not open Arduino serial port {self.port}: {e}. Running in DISCONNECTED mode.")
            self.is_connected = False

    def send_message(self, message: str) -> bool:
        if not self.is_connected or not self.serial_conn or not self.serial_conn.is_open:
            return False
        try:
            self.serial_conn.write(message.encode("utf-8"))
            self.serial_conn.flush()
            return True
        except Exception as e:
            logger.error(f"Error sending to Arduino: {e}")
            self.is_connected = False
            return False

    async def _read_loop(self):
        while self._running:
            if self.is_connected and self.serial_conn and self.serial_conn.is_open:
                try:
                    line = await asyncio.to_thread(self.serial_conn.readline)
                    if line:
                        decoded = line.decode("utf-8", errors="ignore").strip()
                        if decoded:
                            msg_type, data = ArduinoProtocol.parse_message(decoded)
                            if self.callback and msg_type:
                                self.callback(msg_type, data)
                except Exception as e:
                    logger.error(f"Serial read error: {e}")
                    self.is_connected = False
            else:
                # Retry connection periodically if not in simulation mode
                if not self.is_simulation:
                    await asyncio.sleep(3.0)
                    await self._connect()
                else:
                    await asyncio.sleep(1.0)
            await asyncio.sleep(0.05)
