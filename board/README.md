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
- `case/sensor_tile.py`: FreeCAD script for the sensor holder tile (see below).
- `tools/magnet_field.py`: field model used to pick the magnet layout.
- `case/magnet_base.py`: FreeCAD script for the piece magnet bases. Run from the repo root
  with `freecadcmd board/case/magnet_base.py`. Writes STEP (tracked) + STL (local) to
  `case/models/`: `magnet_base_9` / `magnet_base_7` (35 mm test puck, 0.6 mm floor, pockets
  6.4 × 3.2 mm open on top) and `magnet_cutter_9` / `magnet_cutter_7` (pockets only, to
  subtract from a piece model).

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
- Bigger magnets aren't an option, only 6 × 3 mm discs. Model in
  `tools/magnet_field.py`. It counts where the field is above the SS443R trip point
  (typ ~13 mT, worst case 20.5 mT).
- Result: spreading the magnets **widens** the area that switches, up to the point where
  the centre drops below the trip point.
- Piece bases are 35 mm (3D printed, magnets embedded mid-print), squares 40 mm.
  Up to 9 magnets per piece (300 on hand). Chip assumed 5 mm below the magnets
  (3 mm board + ~1 mm inside the sensor + ~0.6 mm printed floor).
- **Chosen layout: 1 centre magnet + ring of 8 at 10 mm radius** (every 45°), all single
  (not stacked), span 26.2 mm. Safe radius ~12.7 mm, centre ~45 mT.
  Ring magnets 1.65 mm apart edge to edge; ring to centre magnet 4 mm edge to edge.
  32 × 9 = 288 magnets (12 spare).
  - Ring radius 9–10 mm is the sweet spot; wider and the centre gets weak.
  - Need more spares: 7 singles in a hex flower at 9 mm pitch, safe radius ~10.5 mm,
    224 magnets (76 spare).
  - Stacking loses here: 2 × 2 stacks of 2 top out at ~9.5 mm safe radius.
  - Most-sensitive sensor reach ~15.6 mm, so a piece would need to sit ~24 mm off-centre
    to trigger the next square's sensor (40 mm away): no crosstalk.
  - Magnets are embedded mid-print. Keep the floor under them thin (2–3 layers).
    Neighbouring magnets repel, so check every magnet's pole before closing it in.
  - Model check: on-axis field matches the textbook cylinder formula. Absolute numbers
    depend on magnet grade (N35 assumed), distance and the sensor's trip point; the bench
    showed a stronger centre than predicted, so treat it as a comparison between layouts.
- Every magnet must have the same pole facing down (the SS443R switches on one pole
  only). Skip Halbach arrays (too fiddly).

## Sensor holder (board underside)
- 8 × 8 squares of 40 mm = 320 × 320 mm. Print bed is 350 mm (~300 mm usable), so the
  holder is **4 identical tiles of 4 × 4 squares (160 × 160 × 20 mm)**.
- One tile = 16 sensors = one MCP23017, mounted in the tile's bays. Only the bus crosses
  between tiles: 5V, 3V3, GND, SDA, SCL.
- Deck 3 mm with a pocket at every square centre (4.4 × 3.4 mm for the 4.1 × 3.1 × 1.6 mm
  sensor, 0.15 mm clearance per side). Sensor lies face up, flush with the deck top, so it
  touches the underside of the 3 mm top sheet. Leads bend straight down through a slot
  on the pocket's -y side.
- Under the deck: perimeter walls + one cross rib make 4 open bays (20 mm tall) for wiring,
  the MCP23017 and (on one tile) the Pico. Wire notches at the bottom of every wall/rib.
  Electronics live under the board, so no frame is needed.
- Tiles bolt together with M3 through the walls (2 per side, same on all sides, so any tile
  fits any corner rotated). The 3 mm sheet rests on top, held by a frame lip or tape.
- Print upside down (deck on the bed): flat top, no supports.

## Open questions
- What should the board do with a move: show it, log it, send it to an app or a chess site?
- Detect only "a piece is here", or also which piece?
- Board size, and how many sensors to read (64 squares needs multiplexing on either chip).
- Does it connect to the clock?
