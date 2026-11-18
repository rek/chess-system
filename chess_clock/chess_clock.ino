// Two-player chess clock on one MAX7219 8-digit display (3 digits per player).
//
// Buttons (each wired between the pin and GND, no resistor needed):
//   Bottom: D4 = Left   D3 = Start/Pause   D2 = Right
//   Top:    D5 = Player 2   D6 = Player 1   (pins swapped to fix the mirrored clock)
//
// READY   : Left/Right step the presets (Left = down, Right = up, wrapping round).
//           A player button starts the OPPONENT's clock. Start begins Player 1's clock.
// RUNNING : Your own player button ends your turn, adds increment, starts opponent's clock.
//           Start pauses. Left/Right also pause (safety).
// PAUSED  : both times blink.
//           1) press a player button on top (sets who resumes: the opponent of that button)
//           2) Left adds 1 min to the left player, Right adds 1 min to the right player
//           3) Start resumes
// FLAGGED : someone hit zero; their time blinks 00.0.
// Hold Start for 1.5 s at any time to reset.
#include <SPI.h>

const uint8_t LOAD_PIN = 10;
const bool REVERSED = false;
const bool UPSIDE_DOWN = false;     // true if the display is mounted rotated 180 degrees
const uint8_t BRIGHTNESS = 4;       // 0-15

// Swap PIN_BTN_LEFT / PIN_BTN_RIGHT if the bottom side buttons are the wrong way round.
const uint8_t PIN_BTN_LEFT = 4, PIN_START = 3, PIN_BTN_RIGHT = 2;
// Swap PIN_P1 / PIN_P2 if the clock is mirrored. (Swapped from the original 6 / 5.)
const uint8_t PIN_P1 = 5, PIN_P2 = 6;

const uint16_t DEBOUNCE_MS = 25;
const uint16_t RESET_HOLD_MS = 1500;

const uint32_t ADD_MS = 60000UL;                 // time added per press while paused
const uint32_t MAX_MS = 99UL * 60000UL;          // display holds at most 99 minutes
const bool REQUIRE_PLAYER_FIRST = true;          // must press a player button before adding time

struct Preset { uint32_t timeMs; uint32_t incMs; };
const Preset PRESETS[] = {
  {180000UL, 2000},   // 3 + 2 (default at power-on)
  {300000UL, 3000},   // 5 + 3
  {600000UL, 5000},   // 10 + 5
};
const uint8_t NUM_PRESETS = sizeof(PRESETS) / sizeof(PRESETS[0]);

// ---------- MAX7219 ----------
void send(uint8_t reg, uint8_t val) {
  digitalWrite(LOAD_PIN, LOW);
  SPI.transfer(reg);
  SPI.transfer(val);
  digitalWrite(LOAD_PIN, HIGH);
}
const uint8_t FONT[16] = {0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B,
                          0x01, 0, 0, 0, 0, 0x00};
uint8_t rot180(uint8_t s) {
  uint8_t r = s & 0x01;
  if (s & 0x40) r |= 0x08;
  if (s & 0x08) r |= 0x40;
  if (s & 0x20) r |= 0x04;
  if (s & 0x04) r |= 0x20;
  if (s & 0x10) r |= 0x02;
  if (s & 0x02) r |= 0x10;
  return r;
}
const uint8_t NUM_DIGITS = 8;
const uint8_t SIDE_START[2] = {0, 5};
uint8_t frameVal[NUM_DIGITS];
bool sepAfter[NUM_DIGITS];

void clearFrame() {
  for (uint8_t i = 0; i < NUM_DIGITS; i++) { frameVal[i] = 0x0F; sepAfter[i] = false; }
}
void flushFrame() {
  bool leftIsReg1 = (UPSIDE_DOWN != REVERSED);
  for (uint8_t v = 0; v < NUM_DIGITS; v++) {
    uint8_t seg = FONT[frameVal[v] & 0x0F];
    bool dot;
    if (UPSIDE_DOWN) {
      seg = rot180(seg);
      dot = (v > 0) && sepAfter[v - 1];
    } else {
      dot = sepAfter[v];
    }
    send(leftIsReg1 ? (v + 1) : (NUM_DIGITS - v), seg | (dot ? 0x80 : 0));
  }
}

// ---------- Buttons ----------
struct Button {
  uint8_t pin;
  bool stable = HIGH, lastRead = HIGH;
  uint32_t changedAt = 0, pressedAt = 0;
  bool pressed = false, released = false;
  Button(uint8_t p) : pin(p) {}
  void update(uint32_t now) {
    bool r = digitalRead(pin);
    pressed = released = false;
    if (r != lastRead) { lastRead = r; changedAt = now; }
    if (now - changedAt >= DEBOUNCE_MS && r != stable) {
      stable = r;
      if (stable == LOW) { pressed = true; pressedAt = now; } else released = true;
    }
  }
  bool down() const { return stable == LOW; }
};
Button bP1(PIN_P1), bP2(PIN_P2), bStart(PIN_START), bLeft(PIN_BTN_LEFT), bRight(PIN_BTN_RIGHT);

// ---------- Clock state ----------
enum State { READY, RUNNING, PAUSED, FLAGGED };
State state = READY;
uint8_t presetIdx = 0;
uint32_t remaining[2];
uint32_t incMs;
uint8_t active = 0;            // whose clock is (or was last) running
uint32_t lastTick = 0;
bool resetFired = false;
bool turnSet = false;          // in PAUSED: a player button has been pressed

void resetClock() {
  remaining[0] = remaining[1] = PRESETS[presetIdx].timeMs;
  incMs = PRESETS[presetIdx].incMs;
  active = 0;
  state = READY;
}

void pauseClock() {
  state = PAUSED;
  turnSet = false;             // must press a player button before adding time
}

void addMinute(uint8_t side) {
  uint32_t t = remaining[side] + ADD_MS;
  remaining[side] = (t > MAX_MS) ? MAX_MS : t;
}

// ---------- Display ----------
void drawTime(uint8_t side, uint32_t ms) {
  uint8_t b = SIDE_START[side];
  if (ms >= 60000UL) {
    uint16_t secs = (ms + 999) / 1000;
    uint8_t mm = secs / 60, ss = secs % 60;
    if (mm >= 10) {
      frameVal[b] = mm / 10; frameVal[b + 1] = mm % 10; sepAfter[b + 1] = true;
      frameVal[b + 2] = ss / 10;
    } else {
      frameVal[b] = mm; sepAfter[b] = true;
      frameVal[b + 1] = ss / 10; frameVal[b + 2] = ss % 10;
    }
  } else {
    uint8_t s = ms / 1000, t = (ms % 1000) / 100;
    frameVal[b] = s / 10; frameVal[b + 1] = s % 10; sepAfter[b + 1] = true;
    frameVal[b + 2] = t;
  }
}

void updateDisplay(uint32_t now) {
  clearFrame();
  bool blinkOff = (state == PAUSED && (now / 500) % 2) ||
                  (state == FLAGGED && (now / 250) % 2);
  for (uint8_t side = 0; side < 2; side++) {
    bool hide = blinkOff && (state == PAUSED || side == active);
    if (!hide) drawTime(side, remaining[side]);
  }
  flushFrame();
}

// ---------- Main ----------
void setup() {
  pinMode(LOAD_PIN, OUTPUT);
  digitalWrite(LOAD_PIN, HIGH);
  pinMode(PIN_P1, INPUT_PULLUP); pinMode(PIN_P2, INPUT_PULLUP);
  pinMode(PIN_START, INPUT_PULLUP);
  pinMode(PIN_BTN_LEFT, INPUT_PULLUP); pinMode(PIN_BTN_RIGHT, INPUT_PULLUP);
  SPI.begin();
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  send(0x0F, 0x00); send(0x0C, 0x01); send(0x0B, 0x07);
  send(0x09, 0x00); send(0x0A, BRIGHTNESS);
  resetClock();
  lastTick = millis();
}

void loop() {
  uint32_t now = millis();
  bP1.update(now); bP2.update(now); bStart.update(now);
  bLeft.update(now); bRight.update(now);

  // Count down the running player's clock.
  uint32_t dt = now - lastTick;
  lastTick = now;
  if (state == RUNNING) {
    if (dt >= remaining[active]) { remaining[active] = 0; state = FLAGGED; }
    else remaining[active] -= dt;
  }

  // Player buttons (top).
  for (uint8_t p = 0; p < 2; p++) {
    Button &b = (p == 0) ? bP1 : bP2;
    if (!b.pressed) continue;
    if (state == READY) { active = 1 - p; state = RUNNING; }
    else if (state == RUNNING && p == active) {
      remaining[p] += incMs;
      active = 1 - p;
    }
    else if (state == PAUSED) {          // no time change, just choose who resumes
      active = 1 - p;
      turnSet = true;
    }
  }

  // Start/Pause: short press toggles, long hold resets.
  if (bStart.pressed) resetFired = false;
  if (bStart.down() && !resetFired && now - bStart.pressedAt >= RESET_HOLD_MS) {
    resetClock(); resetFired = true;
  }
  if (bStart.released && !resetFired) {
    if (state == READY) { active = 0; state = RUNNING; }
    else if (state == RUNNING) pauseClock();
    else if (state == PAUSED) state = RUNNING;
  }

  // Left / Right buttons (bottom).
  if (bLeft.pressed || bRight.pressed) {
    if (state == RUNNING) {
      pauseClock();                                    // safety: any bottom button pauses
    } else if (state == PAUSED) {
      if (!REQUIRE_PLAYER_FIRST || turnSet) {
        addMinute(bLeft.pressed ? 0 : 1);              // left button -> left player
      }
    } else if (state == READY) {
      if (bRight.pressed) presetIdx = (presetIdx + 1) % NUM_PRESETS;
      else presetIdx = (presetIdx + NUM_PRESETS - 1) % NUM_PRESETS;
      resetClock();
    }
  }

  static uint32_t lastDraw = 0;
  if (now - lastDraw >= 50) { lastDraw = now; updateDisplay(now); }
}