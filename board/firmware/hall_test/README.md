# Hall sensor test

Checks one SS443R sensor on the Pico: prints `MAGNET` / `clear` as a magnet comes and goes,
and lights the Pico's on-board LED while a magnet is detected.

## Wiring
Sensor's printed face toward you, legs down, left to right:

| Sensor leg | Pico |
|---|---|
| 1, supply | VBUS (pin 40), 5 V while on USB |
| 2, ground | GND (pin 38) |
| 3, output | GP15 (pin 20), plus 10 kΩ from GP15 to 3V3(OUT) (pin 36) |

The 10 kΩ is optional for this test: the code turns on the Pico's internal pull-up.

## Run
1. Install MicroPython on the Pico: hold BOOTSEL, plug in USB, drag the Pico `.uf2` from
   micropython.org/download/RPI_PI_PICO onto the RPI-RP2 drive.
2. From the repo root: `mpremote run board/firmware/hall_test/main.py`
   (install with `pipx install mpremote` if needed).

## What to note
- Which side of the magnet triggers it (the SS443R reacts to one pole only).
- The distance it switches at, and through how much board material. That sets the
  board thickness.
