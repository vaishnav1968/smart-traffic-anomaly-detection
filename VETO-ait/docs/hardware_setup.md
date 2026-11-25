# VETO Hardware Setup & Wiring Guide

This guide documents the physical human-control interface for **VETO** using an **Arduino Uno R3**.

---

## 1. Required Components

| Component | Quantity | Specification / Notes |
| :--- | :--- | :--- |
| **Microcontroller** | 1 | Arduino Uno R3 (ATmega328P) |
| **Display** | 1 | 0.96-inch SSD1306 OLED (128x64 pixels, I2C, 5V compatible) |
| **Approve Button** | 1 | Momentary push button (Normally Open) |
| **Reject Button** | 1 | Momentary push button (Normally Open) |
| **Emergency Stop Button** | 1 | Push button / mushroom switch |
| **Indicator LED** | 1 | Common-Cathode RGB LED |
| **Current Limiting Resistors** | 3 | 220 $\Omega$ 1/4W resistors |
| **Prototyping** | 1 | Half-size or full-size breadboard |
| **Wiring** | ~15 | Male-to-Male jumper wires |
| **Connection Cable** | 1 | USB Type-A to Type-B cable |

---

## 2. Pinout & Wiring Connections

### A. SSD1306 OLED Display (I2C)

| OLED Pin | Arduino Uno R3 Pin | Function |
| :--- | :--- | :--- |
| **VCC** | `5V` | 5V Power Supply |
| **GND** | `GND` | Ground |
| **SCL** | `A5` (or dedicated SCL) | I2C Clock |
| **SDA** | `A4` (or dedicated SDA) | I2C Data |

*Default I2C Address:* `0x3C`

---

### B. Control Push Buttons (Internal Pull-Up)

All buttons are configured with `INPUT_PULLUP` in firmware. When pressed, the pin is pulled to `GND`.

| Button | Arduino Uno Pin | Wiring Description |
| :--- | :--- | :--- |
| **APPROVE (Green / Blue)** | `Digital Pin 2` | One terminal to `D2`, other terminal to `GND` |
| **REJECT (Red / Orange)** | `Digital Pin 3` | One terminal to `D3`, other terminal to `GND` |
| **EMERGENCY STOP (Red)** | `Digital Pin 4` | One terminal to `D4`, other terminal to `GND` |

---

### C. RGB Indicator LED (Common-Cathode)

| LED Pin | Series Resistor | Arduino Uno Pin | Output Signal |
| :--- | :--- | :--- | :--- |
| **Red Anode** | $220\ \Omega$ | `Digital Pin 9` | PWM (Red channel) |
| **Common Cathode** | None (Direct) | `GND` | Ground |
| **Green Anode** | $220\ \Omega$ | `Digital Pin 10` | PWM (Green channel) |
| **Blue Anode** | $220\ \Omega$ | `Digital Pin 11` | PWM (Blue channel) |

---

## 3. LED Status Table

| System State | LED Color | Meaning |
| :--- | :--- | :--- |
| **Nominal Operation** | **Solid Green** | System healthy, zero-trust policies active |
| **Review Pending** | **Solid Amber / Yellow** | High-risk operation awaiting physical authorization |
| **Approved Feedback** | **Quick Green Pulse** | Operation approved by human |
| **Rejected Feedback** | **Solid Red** | Operation blocked / rejected by human |
| **Emergency Stop** | **Flashing Red** | Emergency stop active, all agent execution halted |

---

## 4. Flashing the Firmware

### Option 1: Using Arduino IDE
1. Open Arduino IDE.
2. Go to **Sketch** -> **Include Library** -> **Manage Libraries...**
3. Install:
   - `Adafruit GFX Library`
   - `Adafruit SSD1306`
4. Open `firmware/veto_controller/veto_controller.ino`.
5. Select **Board: Arduino Uno** and the matching **COM Port** (e.g. `COM3`).
6. Click **Upload** (Ctrl+U).

### Option 2: Using Arduino CLI
```bash
arduino-cli compile --fqbn arduino:avr:uno firmware/veto_controller/
arduino-cli upload -p COM3 --fqbn arduino:avr:uno firmware/veto_controller/
```

---

## 5. Host Communication Protocol

Serial Baudrate: `115200 bps`, 8 data bits, no parity, 1 stop bit (`8N1`).

### Host to Arduino Commands:
- `STATUS:<text>` — Updates idle status banner on OLED.
- `PENDING:<id>:<operation>:<target>` — Displays pending review card on OLED and turns LED amber.
- `DECISION:<id>:<APPROVED|REJECTED>` — Displays decision result on OLED.
- `PING:<nonce>` — Heartbeat probe from host.
- `ESTOP_RESET` — Resets emergency stop state.

### Arduino to Host Events:
- `READY` — Sent on boot.
- `APPROVE:<id>` — Sent when APPROVE button is pressed.
- `REJECT:<id>` — Sent when REJECT button is pressed.
- `ESTOP` — Sent when EMERGENCY STOP button is triggered.
- `PONG:<nonce>` — Sent in response to host PING.
- `HEARTBEAT` — Sent every 3 seconds.

---

## 6. Disconnected Hardware Fallback Mode

If testing on a workstation without a physical Arduino connected:
- Set `ARDUINO_SIMULATION_MODE=true` in `.env`.
- VETO automatically switches to **DISCONNECTED / SIMULATION MODE**.
- The Web Dashboard provides the secondary human-approval controls, allowing full functional testing without hardware.
- Real hardware status is reported explicitly on the dashboard (never falsified).
