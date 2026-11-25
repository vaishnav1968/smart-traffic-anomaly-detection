/**
 * VETO Hardware Controller Firmware
 * Platform: Arduino Uno R3 (ATmega328P)
 * 
 * Hardware Peripherals:
 * - 0.96" SSD1306 OLED (128x64 I2C, Address 0x3C): SDA -> A4, SCL -> A5
 * - APPROVE Button (Momentary NO): Pin 2 (INPUT_PULLUP)
 * - REJECT Button (Momentary NO): Pin 3 (INPUT_PULLUP)
 * - EMERGENCY STOP Button (NC Safety Switch): Pin 4 (INPUT_PULLUP)
 * - RGB LED (Common Cathode with 220 Ohm series resistors):
 *     Red:   Pin 9  (PWM)
 *     Green: Pin 10 (PWM)
 *     Blue:  Pin 11 (PWM)
 * 
 * Serial Protocol (115200 Baud):
 * Host -> Arduino:
 *   STATUS:<text>                Update idle display status text
 *   PENDING:<id>:<op>:<target>   New operation pending review
 *   DECISION:<id>:<state>        Result of review (APPROVED / REJECTED)
 *   PING:<nonce>                 Heartbeat request from host
 *   ESTOP_RESET                  Reset emergency stop lock
 * 
 * Arduino -> Host:
 *   READY                        Device booted and ready
 *   APPROVE:<id>                 Approve button pressed
 *   REJECT:<id>                  Reject button pressed
 *   ESTOP                        Emergency stop button pressed / open
 *   PONG:<nonce>                 Heartbeat response to host
 *   HEARTBEAT                    Periodic keepalive
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pin Definitions
const int PIN_BTN_APPROVE = 2;
const int PIN_BTN_REJECT  = 3;
const int PIN_BTN_ESTOP   = 4;

const int PIN_LED_RED   = 9;
const int PIN_LED_GREEN = 10;
const int PIN_LED_BLUE  = 11;

// Debounce timing
const unsigned long DEBOUNCE_DELAY_MS = 50;
unsigned long lastDebounceTimeApprove = 0;
unsigned long lastDebounceTimeReject  = 0;
unsigned long lastDebounceTimeEstop   = 0;

int lastBtnStateApprove = HIGH;
int lastBtnStateReject  = HIGH;
int lastBtnStateEstop   = HIGH;

int btnStateApprove = HIGH;
int btnStateReject  = HIGH;
int btnStateEstop   = HIGH;

// System States
enum SystemState {
  STATE_NORMAL,
  STATE_PENDING_APPROVAL,
  STATE_DECISION_FEEDBACK,
  STATE_EMERGENCY_STOP
};

SystemState currentState = STATE_NORMAL;

// Pending Operation Details
char currentApprovalId[16] = "";
char currentOperation[16]  = "";
char currentTarget[24]     = "";
char systemStatusText[32]  = "SYSTEM NOMINAL";
char lastDecisionText[16]  = "";

unsigned long feedbackTimer = 0;
unsigned long lastHeartbeatSend = 0;

void setLEDColor(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_LED_RED, r);
  analogWrite(PIN_LED_GREEN, g);
  analogWrite(PIN_LED_BLUE, b);
}

void updateOLED() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Top Banner
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print(F("VETO RUNTIME GUARD"));
  display.drawLine(0, 9, 127, 9, SSD1306_WHITE);

  if (currentState == STATE_EMERGENCY_STOP) {
    display.setTextSize(2);
    display.setCursor(8, 16);
    display.print(F("!! ESTOP !!"));
    display.setTextSize(1);
    display.setCursor(0, 38);
    display.print(F("EXECUTION HALTED"));
    display.setCursor(0, 50);
    display.print(F("Reset via Admin Dashboard"));
  }
  else if (currentState == STATE_PENDING_APPROVAL) {
    display.setTextSize(1);
    display.setCursor(0, 13);
    display.print(F("REQ: "));
    display.print(currentApprovalId);

    display.setCursor(0, 24);
    display.print(F("OP:  "));
    display.print(currentOperation);

    display.setCursor(0, 35);
    display.print(F("TGT: "));
    display.print(currentTarget);

    display.drawLine(0, 48, 127, 48, SSD1306_WHITE);
    display.setCursor(4, 52);
    display.print(F("[APPROVE]   [REJECT]"));
  }
  else if (currentState == STATE_DECISION_FEEDBACK) {
    display.setTextSize(2);
    display.setCursor(12, 18);
    display.print(lastDecisionText);

    display.setTextSize(1);
    display.setCursor(0, 40);
    display.print(F("ID: "));
    display.print(currentApprovalId);
    display.setCursor(0, 52);
    display.print(F("Decision enforced."));
  }
  else { // STATE_NORMAL
    display.setTextSize(1);
    display.setCursor(0, 16);
    display.print(F("STATUS: "));
    display.print(systemStatusText);

    display.setCursor(0, 30);
    display.print(F("ZERO-TRUST ACTIVE"));

    display.setCursor(0, 44);
    display.print(F("Mode: Hardware Leased"));

    display.setCursor(0, 56);
    display.print(F("Audit Chain: SYNCED"));
  }

  display.display();
}

void processIncomingCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd.startsWith("STATUS:")) {
    String txt = cmd.substring(7);
    txt.toCharArray(systemStatusText, sizeof(systemStatusText));
    if (currentState == STATE_NORMAL) updateOLED();
  }
  else if (cmd.startsWith("PENDING:")) {
    // Format: PENDING:<id>:<operation>:<target>
    int idx1 = cmd.indexOf(':', 8);
    int idx2 = cmd.indexOf(':', idx1 + 1);

    if (idx1 > 0 && idx2 > 0) {
      String id = cmd.substring(8, idx1);
      String op = cmd.substring(idx1 + 1, idx2);
      String tgt = cmd.substring(idx2 + 1);

      id.toCharArray(currentApprovalId, sizeof(currentApprovalId));
      op.toCharArray(currentOperation, sizeof(currentOperation));
      tgt.toCharArray(currentTarget, sizeof(currentTarget));

      currentState = STATE_PENDING_APPROVAL;
      // Yellow LED for pending review
      setLEDColor(255, 180, 0);
      updateOLED();
    }
  }
  else if (cmd.startsWith("DECISION:")) {
    // Format: DECISION:<id>:<decision>
    int idx = cmd.indexOf(':', 9);
    if (idx > 0) {
      String id = cmd.substring(9, idx);
      String dec = cmd.substring(idx + 1);

      dec.toCharArray(lastDecisionText, sizeof(lastDecisionText));
      currentState = STATE_DECISION_FEEDBACK;
      feedbackTimer = millis();

      if (dec == "APPROVED") {
        setLEDColor(0, 255, 0); // Solid Green
      } else {
        setLEDColor(255, 0, 0); // Solid Red
      }
      updateOLED();
    }
  }
  else if (cmd.startsWith("PING:")) {
    String nonce = cmd.substring(5);
    Serial.print(F("PONG:"));
    Serial.println(nonce);
  }
  else if (cmd == "ESTOP_RESET") {
    currentState = STATE_NORMAL;
    setLEDColor(0, 255, 0);
    updateOLED();
  }
}

void checkButtons() {
  unsigned long now = millis();

  // 1. APPROVE Button
  int readingApprove = digitalRead(PIN_BTN_APPROVE);
  if (readingApprove != lastBtnStateApprove) {
    lastDebounceTimeApprove = now;
  }
  if ((now - lastDebounceTimeApprove) > DEBOUNCE_DELAY_MS) {
    if (readingApprove != btnStateApprove) {
      btnStateApprove = readingApprove;
      if (btnStateApprove == LOW && currentState == STATE_PENDING_APPROVAL) {
        Serial.print(F("APPROVE:"));
        Serial.println(currentApprovalId);
      }
    }
  }
  lastBtnStateApprove = readingApprove;

  // 2. REJECT Button
  int readingReject = digitalRead(PIN_BTN_REJECT);
  if (readingReject != lastBtnStateReject) {
    lastDebounceTimeReject = now;
  }
  if ((now - lastDebounceTimeReject) > DEBOUNCE_DELAY_MS) {
    if (readingReject != btnStateReject) {
      btnStateReject = readingReject;
      if (btnStateReject == LOW && currentState == STATE_PENDING_APPROVAL) {
        Serial.print(F("REJECT:"));
        Serial.println(currentApprovalId);
      }
    }
  }
  lastBtnStateReject = readingReject;

  // 3. EMERGENCY STOP Button
  // Assuming momentary/latching button pressed to pull LOW or break circuit
  int readingEstop = digitalRead(PIN_BTN_ESTOP);
  if (readingEstop != lastBtnStateEstop) {
    lastDebounceTimeEstop = now;
  }
  if ((now - lastDebounceTimeEstop) > DEBOUNCE_DELAY_MS) {
    if (readingEstop != btnStateEstop) {
      btnStateEstop = readingEstop;
      if (btnStateEstop == LOW) {
        currentState = STATE_EMERGENCY_STOP;
        setLEDColor(255, 0, 0); // Flashing Red
        updateOLED();
        Serial.println(F("ESTOP"));
      }
    }
  }
  lastBtnStateEstop = readingEstop;
}

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  while (!Serial && millis() < 1000);

  // Pin Modes
  pinMode(PIN_BTN_APPROVE, INPUT_PULLUP);
  pinMode(PIN_BTN_REJECT,  INPUT_PULLUP);
  pinMode(PIN_BTN_ESTOP,   INPUT_PULLUP);

  pinMode(PIN_LED_RED,   OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_BLUE,  OUTPUT);

  // Initial Green
  setLEDColor(0, 255, 0);

  // Initialize I2C OLED
  Wire.begin();
  if (display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(18, 20);
    display.println(F("VETO SECURITY"));
    display.setCursor(20, 35);
    display.println(F("INITIALIZING..."));
    display.display();
    delay(500);
  }

  currentState = STATE_NORMAL;
  updateOLED();

  // Announce ready to host
  Serial.println(F("READY"));
}

void loop() {
  // Check buttons
  checkButtons();

  // Handle serial input from host
  if (Serial.available() > 0) {
    String incoming = Serial.readStringUntil('\n');
    processIncomingCommand(incoming);
  }

  // Handle feedback display timeout (return to normal state after 2.5s)
  if (currentState == STATE_DECISION_FEEDBACK) {
    if (millis() - feedbackTimer > 2500) {
      currentState = STATE_NORMAL;
      setLEDColor(0, 255, 0); // Return to Green
      updateOLED();
    }
  }

  // Periodic Heartbeat every 3 seconds
  if (millis() - lastHeartbeatSend > 3000) {
    lastHeartbeatSend = millis();
    Serial.println(F("HEARTBEAT"));
  }
}
