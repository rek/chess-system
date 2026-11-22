# One sensor tile test: 16 SS443R -> MCP23017 (0x20) -> Raspberry Pi Pico (MicroPython).
# Wiring: board/schematic/tile.pdf. Prints the 4 x 4 grid every time a square changes,
# and lights the Pico's LED while any square has a piece.
#
# GPA7 / GPB7 (squares d2, d4): Microchip says these are output-only (datasheet rev D), since
# an input changing during an I2C read can corrupt SDA. To catch that, every read is done
# twice and only accepted when both agree. "bad reads" counts how often they didn't.

from machine import Pin, I2C
import time

ADDR = 0x20
IODIRA, GPPUA, GPIOA = 0x00, 0x0C, 0x12   # BANK=0 register map; A and B are consecutive

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
led = Pin("LED", Pin.OUT)

found = i2c.scan()
print("I2C devices:", [hex(a) for a in found])
if ADDR not in found:
    raise SystemExit("MCP23017 not found at 0x20: check VCC, GND, SDA/SCL, RESET to 3V3, A0-A2 to GND")

i2c.writeto_mem(ADDR, IODIRA, b"\xff\xff")   # all 16 pins inputs (the default, set anyway)
i2c.writeto_mem(ADDR, GPPUA, b"\xff\xff")    # built-in pull-ups on (~100k to 3.3 V)

# bit i of the 16-bit value (GPA = bits 0-7, GPB = bits 8-15) -> square
SQUARES = [f + str(r) for r in range(1, 5) for f in "abcd"]   # a1 b1 c1 d1 a2 ... d4

def read_raw():
    a, b = i2c.readfrom_mem(ADDR, GPIOA, 2)
    return a | (b << 8)

bad_reads = 0
def read_pieces():
    """Bitmask of squares with a piece (sensor output LOW = magnet)."""
    global bad_reads
    while True:
        try:
            x, y = read_raw(), read_raw()
        except OSError:
            bad_reads += 1
            continue
        if x == y:
            return ~x & 0xFFFF
        bad_reads += 1

def show(mask):
    print()
    for r in range(4, 0, -1):
        row = " ".join("#" if mask >> ((r - 1) * 4 + c) & 1 else "." for c in range(4))
        print(f" {r}  {row}")
    print("    a b c d    pieces: %d   bad reads: %d" % (bin(mask).count("1"), bad_reads))

print("Tile test running. Put a piece on each square in turn.")
last = None
while True:
    m = read_pieces()
    if m != last:
        if last is not None:
            for i in range(16):
                if (m ^ last) >> i & 1:
                    print("%8d ms  %s %s" % (time.ticks_ms(), SQUARES[i], "ON " if m >> i & 1 else "off"))
        show(m)
        led.value(m != 0)
        last = m
    time.sleep_ms(20)
