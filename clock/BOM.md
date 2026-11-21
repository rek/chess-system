# Bill of materials: chess clock

Prices left blank to fill in. The case and seesaw are 3D printed (not counted here).

## Clock

| Qty | Part | Notes | Unit price | Total |
|---:|---|---|---:|---:|
| 1 | Arduino Nano (clone) | ATmega328P, 5V, CH340 USB, old bootloader | Rs. 1,450 | Rs. 1,450 |
| 1 | MAX7219 8-digit 7-segment display module (2 × 4-digit displays) | SPI: DIN D11, LOAD D10, CLK D13 | Rs. 285 | Rs. 285 |
| 2 | End stop switch (microswitch) | Under each end of the seesaw: Player 1 on D5, Player 2 on D6 | Rs. 160 | Rs. 320 |
| 3 | Push button (momentary) | Bottom row: Left D4, Start/Pause D3, Right D2 | Rs. 50 | Rs. 150 |
| 12 | Magnet, 6 × 3 mm | Bought as a pack of 12 | Rs. 120 (pack) | Rs. 120 |
| 1 | Buzzer, active (HYDZ) | Beeps when a player runs out of time: + to D9, - to GND | | |
| 2 | LED | One per player, shows whose turn it is (not in firmware yet) | | |
| 2 | Resistor, 330 Ω | Current limit for the LEDs (about 9 mA at 5V) | | |
| 10 | M3 heat-set screw insert | | | |
| 10 | M3 screw | Length to match the case | | |
| 1 m | Hook-up wire | Buttons, switches, display, LEDs | | |
| | **Total (priced so far)** | | | **Rs. 2,325** |

## Power (planned, not built yet)

| Qty | Part | Notes | Unit price | Total |
|---:|---|---|---:|---:|
| 1 | Seeed Lipo Rider Plus (v1.1) | 5V boost, on/off switch. Its own charger is NOT used (too fast) | | |
| 1 | TP4056 module (HW-373, USB-C, with protection) | Charges the cell at its stock 1A; protects it | | |
| 1 | LiPo cell, 1200 mAh, 3.7V | Check plug polarity and max charge rate (see README.md) | | |
| 1 | 1N5817 Schottky diode | Rider 5V to Nano 5V, stripe toward the Nano | | |
| | **Total** | | | |

## 3D printing

| Part | Cost |
|---|---:|
| Case, seesaw and button covers (all printed parts, estimate) | Rs. 500 |

## Grand total

| Section | Cost |
|---|---:|
| Clock parts (priced so far) | Rs. 2,325 |
| 3D printing (estimate) | Rs. 500 |
| **Total** | **Rs. 2,825** |

Not yet priced: LEDs, resistors, M3 inserts and screws, wire, and the planned power parts.

## Notes
- Buttons and switches need no resistors: the Nano's internal pull-ups are used.
- The LEDs need two free pins (for example D7 and D8) and a firmware change.
