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

## Battery plan (not built yet)
- Parts: Seeed LiPo Rider Plus (charger + 5V boost, USB-C charging, on/off switch) and a 600 mAh LiPo.
  Replaces the earlier TP4056 + boost idea (the TP4056 only charges; a single cell is 3.0-4.2V,
  too low for the ATmega328P at 16 MHz and the MAX7219, which want about 4.5-5V).
- Wiring: LiPo -> Rider battery connector. Rider 5V out -> Nano 5V pin. Rider GND -> Nano GND.
  Use the Rider's switch as the clock's power switch.
- Runtime estimate: about 6-10 h (roughly 80 mA from the cell). Unmeasured.
- BEFORE POWERING UP:
  - Check LiPo plug polarity against the Rider's +/- markings. Plugs are not standardized and a
    reversed cell can destroy the board.
  - Check the Rider's charge current against the cell's max charge rate (600 mA or less is typical
    for 600 mAh). Check Seeed's wiki for whether it can be lowered.
  - The 5V pin bypasses the Nano's USB protection: switch the Rider OFF before plugging USB into the Nano.
  - Pad labels above are from memory; confirm against Seeed's wiki.
- Open: cell connector type and max charge rate (read the label).

## Next steps
1. Plug in the Nano, upload `chess_clock`, wire the 4 buttons, test all states.
2. Decide on a second display or alternating display for both clocks.
3. Battery: confirm connector, polarity and charge rate, then build the power path.
4. Later: assess staying on the Nano vs moving to the Pico for the chessboard.

## Ideas / not done
- Buzzer on flag, LEDs for whose turn it is.

