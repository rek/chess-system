// MAX7219 4-digit display test. No library: raw SPI, ~20 lines of driver.
// Wiring: DIN->D11, CLK->D13, LOAD->D10, VCC->5V, GND->GND (use the DIN side!)
#include <SPI.h>

const uint8_t LOAD_PIN = 10;
// If digits show up backwards, flip this to true.
const bool REVERSED = false;

void send(uint8_t reg, uint8_t val) {
  digitalWrite(LOAD_PIN, LOW);
  SPI.transfer(reg);
  SPI.transfer(val);
  digitalWrite(LOAD_PIN, HIGH);
}

// pos 0 = leftmost digit. value: 0-9, 0x0F = blank, 0x0A = '-'. dot lights the decimal point.
void setDigit(uint8_t pos, uint8_t value, bool dot = false) {
  uint8_t reg = REVERSED ? (4 - pos) : (pos + 1);   // registers 1..4
  send(reg, value | (dot ? 0x80 : 0));
}

void clearAll() { for (uint8_t i = 0; i < 4; i++) setDigit(i, 0x0F); }

// Shows mm.ss with the dot standing in for the colon (module has no colon).
void showTime(uint8_t mm, uint8_t ss) {
  setDigit(0, mm / 10);
  setDigit(1, mm % 10, true);
  setDigit(2, ss / 10);
  setDigit(3, ss % 10);
}

void showNumber(uint16_t n) {
  for (int8_t i = 3; i >= 0; i--) { setDigit(i, n % 10); n /= 10; }
}

void setup() {
  pinMode(LOAD_PIN, OUTPUT);
  digitalWrite(LOAD_PIN, HIGH);
  SPI.begin();
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));

  send(0x0F, 0x00);  // display test off
  send(0x0C, 0x01);  // normal operation (not shutdown)
  send(0x0B, 0x03);  // scan limit: digits 0-3 only
  send(0x09, 0xFF);  // decode mode: BCD for all digits
  send(0x0A, 0x04);  // brightness 0-15
  clearAll();
}

void loop() {
  showNumber(1234);   delay(2000);   // test 1
  showTime(10, 0);    delay(2000);   // test 2: "10.00"
  clearAll();         delay(1000);   // test 3: clear
  setDigit(0, 1);     delay(500);    // test 4: digits one at a time
  setDigit(1, 2);     delay(500);
  setDigit(2, 3);     delay(500);
  setDigit(3, 4);     delay(500);
  setDigit(3, 9);     delay(1000);   // update a single digit
  for (uint8_t b = 0; b < 16; b++) { send(0x0A, b); delay(150); }  // brightness sweep
  send(0x0A, 0x04);
}
