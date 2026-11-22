# Tile test

Checks one printed sensor tile: 16 SS443R sensors, one MCP23017, and the Pico. Prints the
4 × 4 grid every time a square changes, and lights the Pico's LED while any square has a
piece.

## Wiring
Schematic: `board/schematic/tile.pdf` (made by `board/schematic/make_tile_schematic.py`).
Wiring map, seen from underneath: `board/schematic/tile_wiring.svg` (made by `make_tile_wiring.py`).

| From | To |
|---|---|
| Pico VBUS (pin 40) | +5V rail: every sensor's leg 1 (VS) |
| Pico GND (pin 38) | GND rail: every sensor's leg 2, MCP23017 GND, A0, A1, A2 |
| Pico 3V3(OUT) (pin 36) | MCP23017 VCC and RESET |
| Pico GP4 (pin 6) | MCP23017 SDA |
| Pico GP5 (pin 7) | MCP23017 SCL |
| Sensor leg 3 (OUT) | MCP23017 pin for its square (below) |

| Square | a | b | c | d |
|---|---|---|---|---|
| row 4 | GPB4 | GPB5 | GPB6 | GPB7 |
| row 3 | GPB0 | GPB1 | GPB2 | GPB3 |
| row 2 | GPA4 | GPA5 | GPA6 | GPA7 |
| row 1 | GPA0 | GPA1 | GPA2 | GPA3 |

Square a1 is the tile corner nearest the bottom-left when the tile sits top up with its lead
slots toward you.

Also fit a 100 nF capacitor across the MCP23017's VCC and GND (skip if the module already
has one) and a 10 µF across +5V and GND on the tile.

## Build order
1. Wire the Pico, MCP23017 and **one** sensor (a1). Run the test: it must find `0x20` and
   show a1 switching.
2. Add the other 15 sensors. Before powering, check every sensor with the multimeter on
   continuity: no beep between any two of its legs.
3. Run the test and put a piece on each square in turn.

## Run
From the repo root: `mpremote run board/firmware/tile_test/main.py`
(MicroPython on the Pico, and `pipx install mpremote`, as in `../hall_test/`).

## What to look for
- Each square switches ON when a piece is placed and off when it's lifted, and no other
  square changes.
- `bad reads` stays at 0 or close to it. If it climbs when you place pieces on d2 or d4,
  that's the GPA7/GPB7 problem (see `board/README.md`).
- Flickering squares: add a 10 kΩ pull-up from that output to 3V3.
