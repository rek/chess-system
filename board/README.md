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

## Test results
- 2026-11-21, one SS443R, 6 × 3 mm magnet, LED test (no code): **works**. Switches on one
  magnet face only, as expected. Also works through a thin piece of wood, but the magnet has
  to be very close and centred over the sensor. Not yet measured: wood thickness, max height,
  how far off-centre it still switches.
- Idea: more or bigger magnets per piece so an off-centre piece still registers.
- 2026-11-22, two 6 × 3 mm magnets stacked (acts as one 6 × 6 mm magnet): **much better
  reach** than one.

## Magnet choice per piece
- Stacking adds reach, with diminishing returns once the stack is taller than it is wide.
- A wider magnet widens the area where an off-centre piece still registers.
- Several magnets side by side give a weaker peak than one solid disc, but the sensor only
  needs to pass its trip point, so spreading them can still give a wider switching area.
- Bigger magnets aren't an option: 8 × (6 × 3 mm) per piece. Model in
  `tools/magnet_field.py`. It counts where the field is above the SS443R trip point
  (typ ~13 mT, worst case 20.5 mT), with the Hall chip 4–5 mm below the magnets
  (3 mm board + ~1 mm inside the sensor package).
- Result: spreading the magnets **widens** the area that switches, up to the point where
  the centre drops below the trip point.
- **Chosen layout: 7 single magnets (not stacked) in a hex "flower"**, 1 in the centre and
  6 around it at 7.5 mm centre-to-centre (1.5 mm gaps), about 21 mm across. Safe radius
  ~10.3 mm, centre ~72 mT. Beats every 8-magnet layout tested, with one fewer magnet.
  32 pieces × 7 = 224 magnets (300 on hand, 76 spare).
  - Base too small for 21 mm: same flower with magnets touching (18 mm), safe radius ~9.5 mm.
  - Budget option: 4 singles in a touching 2 × 2 square (14.5 mm), safe radius ~7.8 mm.
  - Field 22 mm away is tiny and the wrong pole, so the neighbouring square won't trigger.
- Every magnet must have the same pole facing down (the SS443R switches on one pole
  only). Skip Halbach arrays (too fiddly).

## Open questions
- What should the board do with a move: show it, log it, send it to an app or a chess site?
- Detect only "a piece is here", or also which piece?
- Board size, and how many sensors to read (64 squares needs multiplexing on either chip).
- Does it connect to the clock?
