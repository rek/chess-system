# Electronic chessboard

Senses where the pieces are so moves can be recorded. The chess clock (`../clock/`) was the
stepping stone for this.

## Hardware (see `BOM.md`)
- Raspberry Pi Pico (RP2040) as the controller.
- 64 Honeywell SS443R Hall-effect sensors, one per square; a magnet in each piece.
- 4 MCP23017 I²C expanders give the 64 inputs (16 each).

## Power and signal levels
- SS443R supply: 5 V from the Pico's VBUS. Listings disagree on its minimum (3 V or 4.5 V),
  so don't run it from 3.3 V.
- Its output is open-collector (only pulls LOW). Pull-ups go to 3.3 V, so the Pico and the
  MCP23017s (run at 3.3 V) never see 5 V.
- Unipolar: switches for one magnet pole only, so all magnets go in the same way up.

## Folders
- `firmware/hall_test/`: one-sensor test on the Pico (MicroPython).

## Status
Testing a single sensor (2026-11-21).

## Open questions
- What should the board do with a move: show it, log it, send it to an app or a chess site?
- Detect only "a piece is here", or also which piece?
- Board size, and how many sensors to read (64 squares needs multiplexing on either chip).
- Does it connect to the clock?
