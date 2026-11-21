# Chess clock prototype

Standalone two-player chess clock, a stepping stone toward a custom electronic chessboard
(Hall-effect sensors + Raspberry Pi Pico). Keep it simple: this is a prototype.

## Folder layout
- Git repo: github.com/rek/chess-system (public). Only the .ino sketches and .md notes are
  tracked; case designs (case.blend, models/*.stl) stay local on purpose.
- `max7219_test/`: display test sketch (1234, 10.00, clear, digits, brightness). **Working.**
- `chess_clock/`: the clock sketch. **Working** on the Nano (tested 2026-11-17).
- `NOTES.md`: this file.

## Build and upload
Board is the Nano with the OLD bootloader, so the FQBN is `arduino:avr:nano:cpu=atmega328old`.

    arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328old chess_clock
    arduino-cli upload  -p /dev/ttyUSB0 --fqbn arduino:avr:nano:cpu=atmega328old chess_clock

(Core `arduino:avr@1.8.8` installed. User is in the `uucp` group, so no sudo.)

## Nano (verified 2026-11-14)
- USB chip: CH340 (`1a86:7523`) -> `/dev/ttyUSB0`.
- MCU signature `1E 95 0F` = ATmega328P (NOT the "B" variant, which reads `1E 95 16`).
- Bootloader: old-style, 57600 baud. No reflashing needed.
- Read signature: `avrdude -v -c arduino -p m328p -P /dev/ttyUSB0 -b 57600 -n`
- Not yet checked by eye: that logic is 5V (classic Nano is).

## Wiring
| Part | Nano pin |
|---|---|
| Display VCC / GND | 5V / GND |
| Display DIN | D11 (MOSI) |
| Display LOAD | D10 |
| Display CLK | D13 (SCK) |
| Right button (bottom) | D2 to GND |
| Start/Pause button (bottom, middle) | D3 to GND |
| Left button (bottom) | D4 to GND |
| Player 1 button (top seesaw, left) | D5 to GND |
| Player 2 button (top seesaw, right) | D6 to GND |

- Buttons need no resistors (internal pull-ups).
- Display: the two 5-pin rows are wired together except DIN/DOUT. Power, LOAD and CLK can come
  from either row. D11 must go to DIN, never DOUT. Confirmed working 2026-11-14.
- The display in the case is an 8-digit MAX7219 module, mounted upright (it was upside down until
  2026-11-17; `UPSIDE_DOWN = true` in the sketch flips it in software if ever needed).
- Upside down, the decimal points sit at the top of the digits, which is why it was remounted.

## Clock behaviour (chess_clock.ino)
- READY: Right (D2) / Left (D4) step up / down through presets 3+2 (default), 5+3, 10+5, wrapping round; the display shows the preset's starting time
  (3.00, 5.00 or 10.0). A player button starts the OPPONENT's clock. Start begins the
  clock of the player whose seesaw side is up (Player 1 if it reads level). A side already
  down at power-on is not treated as a press.
- RUNNING: your own button ends your turn, adds increment, starts the opponent's clock.
  Start pauses. Left/Right also pause.
- PAUSED: both times blink.
  - Left/Right short press: +1 min to that side's player. Long press (0.7 s): -1 min, to undo a mistake.
  - Player button: ends that player's turn with no increment (rock the seesaw back to hand the turn back).
  - Start resumes the player whose seesaw side is up.
  - Illegal move: offender presses their side, someone pauses, +1 min on the side that gets it,
    rock the seesaw back to the offender, Start resumes the offender's clock.
- FLAGGED: the player at zero blinks `00.0`.
- Hold Start 1.5 s anytime to reset.
- Display: Player 1 on the left 3 digits, Player 2 on the right 3, the two middle digits blank.
  Format `MM.S` (10 min+, S = tens of seconds), `M.SS` (under 10 min), `SS.t` (under 1 min).
- Display digits backwards? Flip `REVERSED` in the sketch.
- Display start-up: kept switched off until it is dim and blank, then switched on. Settings
  are resent every second so a voltage dip that knocks it into test mode (all 888) recovers.
  `BRIGHTNESS = 1` (was 4) to keep current low on battery.

## Battery plan (not built yet, updated 2026-11-21)
Schematics: `power/power_simple.kicad_sch` (chosen) and `power/power.kicad_sch` (alternative),
with PDFs. Kept local, not in git.
- Parts: 1200 mAh LiPo, TP4056 module (HW-373: 4056E charger + DW01/8205A protection, has
  OUT+/OUT-), Seeed Lipo Rider Plus (board rev v1.1, ETA9740 chip), 1N5817 Schottky diode.
- Why the TP4056 stays: the Rider Plus charges at up to 2A (Seeed; the ETA9740 can do 3A, exact
  setting unknown), too fast for small cells. The TP4056 at its stock 1A suits 1200 mAh, so no
  resistor swap. Measure R3 first: about 1.2k = 1A. A cell under 1000 mAh would need R3 = 4.7k.
  The Rider also has no cell protection of its own; the TP4056 module provides it.
- Wiring: cell -> TP4056 B+/B-. TP4056 OUT+/OUT- -> Rider JST (marked: - top, + bottom).
  Rider header 5V (pin 5) -> D1 (stripe to Nano) -> Nano 5V pin. Rider GND -> Nano GND.
  Rider OFF/ON slide switch = clock power switch.
- Rider header, from the square pad: 1 USB, 2 GND, 3 BAT, 4 GND, 5 5V, 6 GND, 7 EN, 8 3V3
  (read off the board, 2026-11-21).
- Charging: USB-C into the TP4056 (needs its own hole in the case). Leave the Rider's USB-C and
  header USB pin EMPTY. The Nano's USB is for uploading only. `power.kicad_sch` shows how to
  charge from the Nano's USB instead (one wire soldered to the USB side of the Nano's diode).
- The Rider Plus boost gives up to 2.4A, so the display's power-on surge (see the AA test below)
  is not a concern.
- Runtime estimate: roughly 10-20 h at brightness 1. Unmeasured.
- BEFORE POWERING UP:
  - Check the cell's plug polarity against the TP4056 B+/B- and the Rider's +/- markings.
  - Check the cell's label for its max charge rate (1A or more is needed with stock R3).
  - Switch the Rider OFF before plugging USB into the Nano.

## Battery test: 2 x AA + small step-up board (tried 2026-11-21, failed)
- 2 x AA (3V) into a small adjustable step-up board, its 5V into the Nano's USB socket.
  Feeding the 5V pin directly doesn't suit this build, so power must go through USB.
- Result: power LED on, display stuck on 888, pulsing. Turning the output up to 5.4V didn't help.
- Cause: at power-on the MAX7219 lights every segment and pulls a current surge before the
  sketch runs. The step-up board can't supply it, its output collapses, and it keeps restarting.
  At 3V in, the cells supply about twice the output current, so AAs sag badly.
- Not a code problem: the 888 appears before the Nano boots. The firmware changes above only
  help once it is running.
- Works fine from a USB power bank (using that for now).
- If retrying AAs: a 470-1000 uF capacitor (10V+) across the step-up output (stripe leg to GND),
  a third AA cell, or a step-up board rated 1A+. Still untested: does the Nano boot on the AAs
  with the display unplugged?

## Next steps
1. Plug in the Nano, upload `chess_clock`, wire the 4 buttons, test all states.
2. Decide on a second display or alternating display for both clocks.
3. Battery: measure TP4056 R3, check cell polarity and charge rate, then build `power_simple`.
4. Later: assess staying on the Nano vs moving to the Pico for the chessboard.

## Ideas / not done
- Buzzer on flag, LEDs for whose turn it is.

