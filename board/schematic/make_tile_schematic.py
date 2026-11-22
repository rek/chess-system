# Generates the KiCad schematic for ONE sensor tile (16 SS443R + 1 MCP23017 + the Pico).
# Run from the repo root:  python3 board/schematic/make_tile_schematic.py
# Then export the PDF:     kicad-cli sch export pdf board/schematic/tile.kicad_sch -o board/schematic/tile.pdf
# Connections are made with net labels: pins with the same label name are wired together.
import uuid, os

OUT = os.path.join("board", "schematic", "tile.kicad_sch")
ROOT = str(uuid.uuid4())
U = lambda: str(uuid.uuid4())
F = '(effects (font (size 1.27 1.27)))'
FH = '(effects (font (size 1.27 1.27)) hide)'

def lib_symbol(name, ref, value, w, h, pins, hide_numbers=True, body=None):
    """pins: list of (number, name, side, offset_y) ; side 'L' or 'R'."""
    out = [f'(symbol "chess:{name}" {"(pin_numbers hide)" if hide_numbers else ""} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
           f'  (property "Reference" "{ref}" (at 0 0 0) {FH})', f'  (property "Value" "{value}" (at 0 0 0) {FH})',
           f'  (property "Footprint" "" (at 0 0 0) {FH})', f'  (property "Datasheet" "" (at 0 0 0) {FH})']
    out.append(body or f'  (symbol "{name}_0_1" (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))')
    ps = []
    for num, pname, side, y in pins:
        x, ang = (-w - 2.54, 0) if side == 'L' else (w + 2.54, 180)
        ps.append(f'(pin passive line (at {x} {y} {ang}) (length 2.54) (name "{pname}" {F}) (number "{num}" {F}))')
    out.append(f'  (symbol "{name}_1_1" ' + ' '.join(ps) + '))')
    return '\n'.join(out), {num: ((-w - 2.54) if side == 'L' else (w + 2.54), y, side) for num, _, side, y in pins}

S = []         # schematic items
LIBS = []
def place(name, pinmap, ref, value, x, y, labels, ref_dy):
    S.append(f'(symbol (lib_id "chess:{name}") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")\n'
             f'  (property "Reference" "{ref}" (at {x} {y - ref_dy} 0) {F})\n  (property "Value" "{value}" (at {x} {y + ref_dy} 0) {F})\n'
             f'  (property "Footprint" "" (at {x} {y} 0) {FH})\n  (property "Datasheet" "" (at {x} {y} 0) {FH})\n  '
             + ' '.join(f'(pin "{n}" (uuid "{U()}"))' for n in pinmap) +
             f'\n  (instances (project "tile" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    for num, net in labels.items():
        px, py, side = pinmap[num]
        ax, ay = round(x + px, 2), round(y - py, 2)
        if net is None:
            S.append(f'(no_connect (at {ax} {ay}) (uuid "{U()}"))'); continue
        ex = round(ax - 5.08, 2) if side == 'L' else round(ax + 5.08, 2)
        S.append(f'(wire (pts (xy {ax} {ay}) (xy {ex} {ay})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        if side == 'L':
            S.append(f'(label "{net}" (at {ex} {ay} 180) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "{U()}"))')
        else:
            S.append(f'(label "{net}" (at {ex} {ay} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')

def text(t, x, y, size=1.27, bold=False):
    t = t.replace('"', '\\"').replace("\n", "\\n")
    S.append(f'(text "{t}" (exclude_from_sim no) (at {x} {y} 0) (effects (font (size {size} {size}){" bold" if bold else ""}) (justify left top)) (uuid "{U()}"))')

# ---------- symbols ----------
pico, pico_p = lib_symbol("PICO", "U1", "Raspberry Pi Pico", 10.16, 7.62,
    [("40", "VBUS(5V)", 'R', 5.08), ("36", "3V3(OUT)", 'R', 2.54), ("38", "GND", 'R', 0),
     ("6", "GP4(I2C0_SDA)", 'R', -2.54), ("7", "GP5(I2C0_SCL)", 'R', -5.08)], hide_numbers=False)
mcp_pins = [("1", "VCC", 'L', 17.78), ("2", "GND", 'L', 15.24), ("3", "SDA", 'L', 10.16), ("4", "SCL", 'L', 7.62),
            ("5", "RESET", 'L', 2.54), ("6", "A0", 'L', -2.54), ("7", "A1", 'L', -5.08), ("8", "A2", 'L', -7.62),
            ("9", "INTA", 'L', -12.7), ("10", "INTB", 'L', -15.24)]
for i in range(8):
    mcp_pins.append((str(11 + i), f"GPA{i}", 'R', 17.78 - 2.54 * i))
    mcp_pins.append((str(19 + i), f"GPB{i}", 'R', -2.54 - 2.54 * i))
mcp, mcp_p = lib_symbol("MCP23017", "U2", "MCP23017 module (addr 0x20)", 10.16, 22.86, mcp_pins)
hall, hall_p = lib_symbol("SS443R", "H", "SS443R", 5.08, 3.81,
    [("1", "VS", 'L', 2.54), ("2", "GND", 'L', -2.54), ("3", "OUT", 'R', 0)], hide_numbers=False)
cap_body = ('  (symbol "CAP_0_1" (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'
            ' (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))))')
cap = (f'(symbol "chess:CAP" (pin_numbers hide) (pin_names (offset 0.254) hide) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
       f'  (property "Reference" "C" (at 0 0 0) {FH})\n  (property "Value" "C" (at 0 0 0) {FH})\n'
       f'  (property "Footprint" "" (at 0 0 0) {FH})\n  (property "Datasheet" "" (at 0 0 0) {FH})\n{cap_body}\n'
       f'  (symbol "CAP_1_1" (pin passive line (at 0 3.81 270) (length 3.048) (name "1" {F}) (number "1" {F}))'
       f' (pin passive line (at 0 -3.81 90) (length 3.048) (name "2" {F}) (number "2" {F}))))')
LIBS += [pico, mcp, hall, cap]

def place_cap(ref, value, x, y, top, bottom):
    S.append(f'(symbol (lib_id "chess:CAP") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")\n'
             f'  (property "Reference" "{ref}" (at {x + 3.81} {y - 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
             f'  (property "Value" "{value}" (at {x + 3.81} {y + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
             f'  (property "Footprint" "" (at {x} {y} 0) {FH})\n  (property "Datasheet" "" (at {x} {y} 0) {FH})\n'
             f'  (pin "1" (uuid "{U()}")) (pin "2" (uuid "{U()}"))\n  (instances (project "tile" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    for py, net, d in ((y - 3.81, top, -5.08), (y + 3.81, bottom, 5.08)):
        S.append(f'(wire (pts (xy {x} {py}) (xy {x} {round(py + d, 2)})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        S.append(f'(label "{net}" (at {x} {round(py + d, 2)} 90) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')

# ---------- placement (A3, mm, 2.54 grid) ----------
place("PICO", pico_p, "U1", "Raspberry Pi Pico (USB powers everything)", 50.8, 76.2,
      {"40": "+5V", "36": "+3V3", "38": "GND", "6": "SDA", "7": "SCL"}, 11.43)
place("MCP23017", mcp_p, "U2", "MCP23017 module, address 0x20", 127.0, 88.9,
      {"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL", "5": "+3V3", "6": "GND", "7": "GND", "8": "GND",
       "9": None, "10": None,
       **{str(11 + i): f"SQ_{'abcd'[i % 4]}{1 + i // 4}" for i in range(8)},
       **{str(19 + i): f"SQ_{'abcd'[i % 4]}{3 + i // 4}" for i in range(8)}}, 26.67)
place_cap("C1", "100nF (at the MCP23017)", 99.06, 132.08, "+3V3", "GND")
place_cap("C2", "10uF (5V rail, on the tile)", 50.8, 132.08, "+5V", "GND")

# sensors: 4 x 4 grid laid out like the squares (row 4 at the top)
for r in range(4):
    for c in range(4):
        sq = f"{'abcd'[c]}{r + 1}"
        x = 205.74 + c * 50.8
        y = 160.02 - r * 33.02
        place("SS443R", hall_p, f"H_{sq}", f"square {sq}", x, y, {"1": "+5V", "2": "GND", "3": f"SQ_{sq}"}, 6.35)

text("ONE SENSOR TILE: 16 Hall sensors (squares a1-d4) -> MCP23017 -> Pico", 25.4, 20.32, 2.54, True)
text("Wires with the same label are connected (e.g. every +5V, every GND, SQ_a1 at the sensor and at GPA0).", 25.4, 27.94)
notes = [
 "1. Power: Pico on USB. VBUS (pin 40) = +5V for the sensors. 3V3(OUT) (pin 36) = +3V3 for the MCP23017. All GNDs together.",
 "2. Sensor legs, printed face toward you, legs down: 1 VS (+5V), 2 GND, 3 OUT. Seen from UNDER the tile (where you solder) the order is mirrored.",
 "3. Sensor outputs only pull LOW. Pull-ups go to +3V3, never +5V. The test firmware turns on the MCP23017's built-in pull-ups (~100k).",
 "   If readings flicker, add a 10k from each SQ_ net to +3V3.",
 "4. MCP23017 RESET must be tied to +3V3 (floating = random resets). A0, A1, A2 to GND = address 0x20 (next tiles: 0x21, 0x22, 0x23).",
 "5. GPA7 and GPB7 (squares d2 and d4): Microchip's datasheet rev D says these are output-only, because an input changing during",
 "   an I2C read can corrupt SDA. Used as inputs here for the test; the firmware reads twice and compares. See board/README.md.",
 "6. INTA/INTB not connected (the Pico polls).",
 "7. Between tiles only 5 wires: +5V, +3V3, GND, SDA, SCL.",
]
for i, n in enumerate(notes):
    text(n, 25.4, 165.1 + 5.08 * i)

doc = [f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")',
       f'(uuid "{ROOT}") (paper "A3")',
       '(title_block (title "Chessboard: one sensor tile") (date "2026-11-22") (rev "A")',
       '  (comment 1 "16 x SS443R -> MCP23017 (0x20) -> Raspberry Pi Pico I2C0"))',
       '(lib_symbols', *LIBS, ')', *S, '(sheet_instances (path "/" (page "1"))))']
open(OUT, "w").write('\n'.join(doc) + '\n')
print("wrote", OUT)
