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
- `firmware/tile_test/`: one-tile test, 16 sensors through one MCP23017 (MicroPython).
- `schematic/make_tile_schematic.py`: generates the KiCad schematic for one tile,
  `schematic/tile.kicad_sch` + `tile.pdf` (local, not tracked). Run from the repo root,
  then `kicad-cli sch export pdf board/schematic/tile.kicad_sch -o board/schematic/tile.pdf`.
- `schematic/make_tile_wiring.py`: to-scale wiring map of one tile seen from underneath
  (where you solder), `schematic/tile_wiring.svg` (local). Open it in a browser.
- `tools/magnet_field.py`: field model used to pick the magnet layout.
- `case/sensor_tile.py`: FreeCAD script for the sensor holder tile (see below). Run from
  the repo root with `freecadcmd board/case/sensor_tile.py`.
- `case/magnet_base.py`: FreeCAD script for the piece magnet bases. Run from the repo root
  with `freecadcmd board/case/magnet_base.py`. Writes STEP (tracked) + STL (local) to
  `case/models/`: `magnet_base_9` / `magnet_base_7` (35 mm test puck, 0.6 mm floor, pockets
  6.4 × 3.2 mm open on top) and `magnet_cutter_9` / `magnet_cutter_7` (pockets only, to
  subtract from a piece model).

## Status
Design stage (2026-11-22): one sensor tested, magnet layout chosen, piece magnet base and
sensor holder tile modelled. Next: print a test tile and a test puck, measure how far
off-centre a piece still switches.

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
- Deck 2.4 mm, a lattice rather than a solid plate: each square keeps a cross of 8 mm arms
  through its sensor and a 3 mm band along its edges, with 4 windows cut out (saves ~40 %
  plastic; the 3 mm sheet spans the windows). A pocket at every square centre
  (4.24 × 3.24 mm for the 4.1 × 3.1 × 1.6 mm sensor, 0.07 mm clearance per side;
  0.15 mm printed ~0.1–0.2 mm loose). Sensor lies face up, flush with the deck top, so it
  touches the underside of the 3 mm top sheet. Leads bend straight down through a slot
  on the pocket's -y side.
- MCP23017 module (CJMCU-2317, 26.7 × 21.5 mm, no mounting holes) snaps into two clips
  under the deck, centred in the a1–b2 bay, long side along x, 5 mm below the deck. Clips
  grip only the middle of its short edges (the long edges carry the pins): a 1 mm flexible
  arm with a 0.5 mm hook, and two stops that touch the board 1 mm in from its edge. Mount
  it labels-out so you can read the pins; check no part on the deck-facing side sits within
  1 mm of the short edges at the middle.
- Wiring the module: solder wires straight into its holes **before** clipping it in (no
  header pins: header + Dupont plugs would stick ~5 mm out below the tile). Trim the solder
  tails on the deck side short, and use **insulated** wire for the 5V/GND rails, which pass
  under the module next to those joints.
- Under the deck: perimeter walls + one cross rib make 4 open bays (20 mm tall) for wiring,
  the MCP23017 and (on one tile) the Pico. Wire notches (12 × 8 mm) in every wall/rib,
  right under the deck, so wires run flat against it.
- Wire clips: 15 pairs of flexible posts on the solid deck bands, forming 3.6 mm channels
  with lips (1 mm gap) that hold a pressed-in bundle. They line 3 trunks: x = 40 (a/b
  columns, rows 3–4, down to the module), x = 120 (c/d columns) and y = 40 (from x = 120
  through the centre rib to the module). See the wiring map.
- The module's 16 inputs are all on one long edge (double row); power, I²C and address
  pins on the other. Fit it inputs-edge towards rows 2–4 (north), so the trunks reach it.
  Electronics live under the board, so no frame is needed.
- Walls and rib are 1.2 mm (3 lines). Each bolt hole sits on a full-height 8 mm pad that
  makes the wall 2.4 mm there.
- Tiles bolt together with M3 through the walls (2 per side, 20 and 140 mm along it,
  same on all sides, so any tile fits any corner rotated). The 3 mm sheet rests on top. With no frame, fix it with
  double-sided tape or a few dots of glue, lined up so its squares sit over the sensors
  (sensor centres are 20 mm in from each tile edge). The sheet must be non-magnetic
  (wood, MDF, acrylic).
- Before printing a full tile, print `sensor_tile_coupon` (one corner square, ~10 g) and
  check a sensor sits snug and flush.
- Print upside down (deck on the bed): flat top, no supports. Turn on elephant-foot
  compensation in the slicer, or the first layers squeeze the pocket openings and the
  sensors won't sit flush.
- Sensor leads: fit the plastic lead covers below the deck (they won't pass the 1.5 mm
  slot). Check every sensor for shorts between legs before wiring the bus.

## Electronics
- **GPA7 / GPB7 problem:** Microchip's MCP23017 datasheet (rev D, June 2022) says GPA7 and
  GPB7 are output-only: an input changing during an I²C read can corrupt SDA. That leaves
  14 safe inputs per chip, 56 for 4 chips, short of 64. The tile test uses them anyway and
  reads twice to catch bad reads. If it shows problems, options: a 5th expander, wire 8
  sensors straight to Pico pins, or swap to TCA9555 modules (16 true inputs, no built-in
  pull-ups, so the 10 kΩ resistors are needed).
- MCP23017 addresses: each of the 4 modules needs its own address, set with its A0–A2
  pads/jumpers: 0x20, 0x21, 0x22, 0x23. Label each tile with its address.
- I²C: the bus runs through all 4 tiles (~0.5 m). Most MCP23017 modules have their own
  SDA/SCL pull-ups; 4 in parallel is fine at 100 kHz.
- Sensor pull-ups: **10 kΩ from every sensor output to 3.3 V** (R1–R16 per tile, 64 in
  all), soldered at the MCP23017 end. The MCP23017's built-in ~100 kΩ pull-ups are too weak
  to rely on: the sensor's allowed output leakage could drag a 100 kΩ line below the chip's
  HIGH threshold. Never pull up to 5 V.
- I²C pull-ups: the module may already have them on SDA/SCL. If the tile test can't find
  0x20, add 4.7 kΩ from SDA and from SCL to 3.3 V (once for the whole bus).
- Power: 64 sensors draw a few hundred mA at 5 V. Fine from USB on the Pico's VBUS, but
  measure it on one tile first. Long-term power source not decided yet.
- Pieces: every magnet has the same pole down, so the board sees only "piece here / not
  here", not which piece. Firmware must track pieces from the starting position, and
  needs another way to choose a promotion piece.

## Open questions
- What should the board do with a move: show it, log it, send it to an app or a chess site?
- How to pick a promotion piece (a button, or the clock's buttons)?
- Long-term power: USB only, or a battery like the clock?
- Does it connect to the clock?
