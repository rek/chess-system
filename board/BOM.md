# Bill of materials: chessboard (proof of concept)

Build: 64-square Hall-effect chessboard. LEDs are not included in this build.

## Main electronics

| Qty | Part | Notes | Status |
|---:|---|---|---|
| 1 | Raspberry Pi Pico (SC0915, RP2040) | Controller | Have |
| 4 | MCP23017 module | 16-bit I²C GPIO expander, 4 × 16 = 64 inputs | Have |
| 64 | Honeywell SS443R Hall-effect sensor | Unipolar on/off switch, open-collector output. Power from 5 V (see README) | Have |
| 300 | Neodymium disc magnet, 6 × 3 mm | 9 per piece: centre + ring of 8 (288 used, 12 spare), see README | Have |

## Passive components

| Qty | Part | Notes | Status |
|---:|---|---|---|
| 100 | Resistor, 10 kΩ, ¼ W | Pull-ups for the sensor outputs, to 3.3 V (never 5 V) | To buy |
| 10 | Ceramic capacitor, 100 nF (104) | Decoupling for the MCP23017 modules | To buy |
| 5 | Electrolytic capacitor, 10 µF, 10 V+ | Bulk decoupling | Optional |

## Wiring and assembly

| Part | Status |
|---|---|
| Pin headers, 2.54 mm male/female | Have |
| Jumper wires (M-M, M-F) | Check |
| Ribbon cable, multi-core | To obtain |
| PCB wire connectors | Optional |
| Perfboard / prototype PCB | Check |

## Printed parts and hardware

| Qty | Part | Notes | Status |
|---:|---|---|---|
| 4 | Sensor tile, 160 × 160 × 20 mm (`case/sensor_tile.py`) | ~55 cm³ (~68 g PLA) each | To print |
| 1 | Top sheet, 3 mm, single piece, ≥ 320 × 320 mm, non-magnetic | Pieces play on this | Check |
| 8 | M3 × 10 bolt + nut | Join the tiles: 2 per shared edge | To buy |

## Tools
Soldering iron and solder, multimeter, PCB fabrication materials (custom sensor boards),
heat-shrink tubing.
