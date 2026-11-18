// Two-player chess clock on one MAX7219 8-digit display (3 digits per player).
//
// Buttons (each wired between the pin and GND, no resistor needed):
//   Bottom: D4 = Left   D3 = Start/Pause   D2 = Right
//   Top:    D5 = Player 1   D6 = Player 2   (seesaw: pressing your side ends your turn)
//
// READY   : Left/Right step the presets 3+2, 5+3, 10+5 (Left = down, Right = up, wrapping
//           round; the display shows that preset's starting time). A player button starts
//           the OPPONENT's clock (you just moved). Start begins Player 1's clock.
// RUNNING : Pressing your own button ends your turn, adds increment, starts opponent's clock.
//           Start pauses. Left/Right also pause (safety).
// PAUSED  : both times blink.
//           Left/Right short press: +1 min to that side's player.
//           Left/Right long press:  -1 min to that side's player (undo a mistake).
//           Player button: ends that player's turn, no increment (so rocking the seesaw back
//           hands the turn back, e.g. after an illegal move).
//           Start resumes whoever is on move.
// FLAGGED : someone hit zero; their time blinks 00.0.
// Hold Start for 1.5 s at any time to reset.
//
// Display: Player 1 on the left 3 digits, Player 2 on the right 3 digits, the two middle
// digits always blank. Format "MM.S" (10 min+, S = tens of seconds), "M.SS" (under 10 min),
// "SS.t" (under 1 min). Power-on preset is 3 + 2.
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

const uint16_t LONG_PRESS_MS = 700;              // Left/Right held this long = -1 min
const uint32_t ADJ_MS = 60000UL;                 // time added/removed per press while paused
const uint32_t MAX_MS = 99UL * 60000UL;          // display holds at most 99 minutes

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
// No-decode mode: we draw segments ourselves so the digits can be turned upside down.
// Bits: DP A B C D E F G = 0x80 ... 0x01. Values 0-9 are digits, 0x0A is '-', 0x0F is blank.
const uint8_t FONT[16] = {0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B,
                          0x01, 0, 0, 0, 0, 0x00};
uint8_t rot180(uint8_t s) {                       // swap A<->D, B<->E, C<->F; G stays
  uint8_t r = s & 0x01;
  if (s & 0x40) r |= 0x08;
  if (s & 0x08) r |= 0x40;
  if (s & 0x20) r |= 0x04;
  if (s & 0x04) r |= 0x20;
  if (s & 0x10) r |= 0x02;
  if (s & 0x02) r |= 0x10;
  return r;
}
// The frame is built in VISUAL positions, 0 = leftmost digit as you look at the clock.
// The 8 digits are split 3 + 1 + 1 + 3: Player 1 uses 0-2, Player 2 uses 5-7,
// and the inner digit on each side (3 and 4) is always blank.
const uint8_t NUM_DIGITS = 8;
const uint8_t SIDE_START[2] = {0, 5};
uint8_t frameVal[NUM_DIGITS];   // FONT index per digit
bool sepAfter[NUM_DIGITS];      // separator dot between digit i and digit i+1

void clearFrame() {
  for (uint8_t i = 0; i < NUM_DIGITS; i++) { frameVal[i] = 0x0F; sepAfter[i] = false; }
}
void flushFrame() {
  // On this module, register 1 is the rightmost digit when upright, so it is the leftmost
  // digit when the module is mounted upside down.
  bool leftIsReg1 = (UPSIDE_DOWN != REVERSED);
  for (uint8_t v = 0; v < NUM_DIGITS; v++) {
    uint8_t seg = FONT[frameVal[v] & 0x0F];
    bool dot;
    if (UPSIDE_DOWN) {
      seg = rot180(seg);
      dot = (v > 0) && sepAfter[v - 1];   // dot is now top-left of a digit, so it shows
    } else {                              // the gap BEFORE that digit
      dot = sepAfter[v];                  // dot is bottom-right: the gap AFTER the digit
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
bool sideArmed[2] = {false, false};   // Left/Right press began while PAUSED
bool sideLongFired[2] = {false, false};

void resetClock() {
  remaining[0] = remaining[1] = PRESETS[presetIdx].timeMs;
  incMs = PRESETS[presetIdx].incMs;
  active = 0;
  state = READY;
}

void addMinute(uint8_t side) {
  if (remaining[side] >= MAX_MS) return;         // never let "add" take time away
  uint32_t t = remaining[side] + ADJ_MS;
  remaining[side] = (t > MAX_MS) ? MAX_MS : t;
}

void subMinute(uint8_t side) {
  if (remaining[side] > ADJ_MS) remaining[side] -= ADJ_MS;   // under a minute: leave it
}

// ---------- Display ----------
// Draws one player's time in their 3 digits:
//   10 minutes or more : "MM.S" (S = tens of seconds)
//   1 to 10 minutes    : "M.SS"
//   under 1 minute     : "SS.t" (tenths)
void drawTime(uint8_t side, uint32_t ms) {
  uint8_t b = SIDE_START[side];
  if (ms >= 60000UL) {
    uint16_t secs = (ms + 999) / 1000;           // round up so 5:00 shows for a full second
    uint8_t mm = secs / 60, ss = secs % 60;
    if (mm >= 10) {                              // "MM.S": S is tens of seconds, so 14:37 = 14.3
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
    // Paused: both sides blink. Flagged: only the player who ran out blinks.
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
  send(0x0F, 0x00); send(0x0C, 0x01); send(0x0B, 0x07);   // scan all 8 digits
  send(0x09, 0x00); send(0x0A, BRIGHTNESS);   // no-decode mode (see FONT)
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
    else if (state == PAUSED) {          // seesaw rocked: hand the turn over, no increment
      active = 1 - p;
    }
  }

  // Start/Pause: short press toggles, long hold resets.
  if (bStart.pressed) resetFired = false;
  if (bStart.down() && !resetFired && now - bStart.pressedAt >= RESET_HOLD_MS) {
    resetClock(); resetFired = true;
  }
  if (bStart.released && !resetFired) {
    if (state == READY) { active = 0; state = RUNNING; }
    else if (state == RUNNING) state = PAUSED;
    else if (state == PAUSED) state = RUNNING;
  }

  // Left / Right buttons (bottom). Left belongs to Player 1, Right to Player 2.
  for (uint8_t side = 0; side < 2; side++) {
    Button &b = (side == 0) ? bLeft : bRight;
    if (b.pressed) {
      // Only a press that STARTS while paused adjusts time, so the press that pauses a
      // running clock doesn't also add a minute when it is released.
      sideArmed[side] = (state == PAUSED);
      sideLongFired[side] = false;
      if (state == RUNNING) state = PAUSED;            // safety: any bottom button pauses
      else if (state == READY) {
        if (side == 1) presetIdx = (presetIdx + 1) % NUM_PRESETS;
        else presetIdx = (presetIdx + NUM_PRESETS - 1) % NUM_PRESETS;
        resetClock();
      }
    }
    if (sideArmed[side] && state == PAUSED) {
      if (b.down() && !sideLongFired[side] && now - b.pressedAt >= LONG_PRESS_MS) {
        subMinute(side); sideLongFired[side] = true;   // long press: -1 min
      }
      if (b.released && !sideLongFired[side]) addMinute(side);   // short press: +1 min
    }
    if (b.released) sideArmed[side] = false;
  }

  static uint32_t lastDraw = 0;
  if (now - lastDraw >= 50) { lastDraw = now; updateDisplay(now); }
}
