# Generates a to-scale wiring map of ONE sensor tile, seen from UNDERNEATH (where you solder).
# Run from the repo root:  python3 board/schematic/make_tile_wiring.py
# Writes board/schematic/tile_wiring.svg (open it in a browser).
# Dimensions follow board/case/sensor_tile.py; connections follow tile.kicad_sch.
import os

OUT = os.path.join("board", "schematic", "tile_wiring.svg")
S, M = 4.0, 40            # px per mm, margin px
SIZE, SQ = 160.0, 40.0
W, H = int(SIZE * S + 2 * M + 430), int(SIZE * S + 2 * M + 150 + 1110)

# underside view: flip left-right (x mirrors), model +y stays up the page
X = lambda x: M + (SIZE - x) * S
Y = lambda y: M + (SIZE - y) * S
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="sans-serif">',
     f'<rect width="{W}" height="{H}" fill="white"/>']
def line(pts, col, w=2.0, dash=None):
    d = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts)
    o.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"'
             + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
def rect(x0, y0, x1, y1, fill="none", stroke="#999", w=1):
    xa, xb = sorted((X(x0), X(x1))); ya, yb = sorted((Y(y0), Y(y1)))
    o.append(f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb-xa:.1f}" height="{yb-ya:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')
def text(x, y, t, size=11, col="#000", anchor="middle", bold=False, raw=False):
    px, py = (x, y) if raw else (X(x), Y(y))
    o.append(f'<text x="{px:.1f}" y="{py:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{" font-weight=\"bold\"" if bold else ""}>{t}</text>')

RED, BLK, SIG, ORG, BLU, GRN = "#d62728", "#222", "#e6a700", "#ff7f0e", "#1f77b4", "#2ca02c"

# ---- tile structure ----
rect(0, 0, SIZE, SIZE, "#f4f4f4", "#555", 2)
rect(79.4, 0, 80.6, SIZE, "#bbb", "#888"); rect(0, 79.4, SIZE, 80.6, "#bbb", "#888")   # cross rib
for k in (40, 120):   # wire notches (bottom of walls/rib)
    for (x, y) in ((k, 0), (k, 80), (k, SIZE)):
        rect(k - 6, y - 1.5, k + 6, y + 1.5, "white", "#555")
    for (x, y) in ((0, k), (80, k), (SIZE, k)):
        rect(x - 1.5, k - 6, x + 1.5, k + 6, "white", "#555")
for k in (20, 140):   # bolt pads
    for (x, y) in ((k, 1.2), (k, SIZE - 1.2)):
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{1.7*S:.1f}" fill="white" stroke="#555"/>')
    for (x, y) in ((1.2, k), (SIZE - 1.2, k)):
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{1.7*S:.1f}" fill="white" stroke="#555"/>')

# ---- MCP23017 pin for each square (same as the schematic) ----
squares = [f + str(r) for r in range(1, 5) for f in "abcd"]
pin_of = {sq: ("GPA%d" % i if i < 8 else "GPB%d" % (i - 8)) for i, sq in enumerate(squares)}

# MCP23017 module (CJMCU-2317, 26.7 x 21.5 mm) snapped into its clips, centred in the a1-b2 bay.
# Drawn last, on top: it sits below the wires that run under it.
MX0, MX1, MY0, MY1 = 26.65, 53.35, 29.25, 50.75

# ---- wire clips (same list as sensor_tile.py) ----
WIRE_CLIPS = ([(40, y, "y") for y in (62, 94, 106, 134)] +
              [(120, y, "y") for y in (26, 54, 66, 94, 106, 134)] +
              [(x, 40, "x") for x in (62, 72, 88, 100, 110)])
def draw_clips():
    for cx, cy, al in WIRE_CLIPS:
        for sd in (-1, 1):
            off = sd * 2.4
            if al == "y":
                rect(cx + off - 0.6, cy - 2, cx + off + 0.6, cy + 2, "#7a4b00", "#3a2400")
            else:
                rect(cx - 2, cy + off - 0.6, cx + 2, cy + off + 0.6, "#7a4b00", "#3a2400")

# ---- module pins (CJMCU-2317): 16 inputs on the NORTH long edge (double row),
#      power / I2C / address on the SOUTH long edge. 10 positions at 2.54 mm along x.
PIN_X = [40 + (k - 4.5) * 2.54 for k in range(10)]   # k = 0 is the VCC/GND end (west)
def gp_x(sq):                                       # GPAn/GPBn share position k = n + 2
    i = squares.index(sq); n = i % 8
    return PIN_X[n + 2] + (0.5 if i >= 8 else -0.5)
NORTH = 50.75

# ---- power rails: spines in the x = 40 and x = 120 trunks, link along the y = 40 trunk ----
line([(38.8, 56), (38.8, 133)], RED, 3); line([(41.2, 56), (41.2, 131)], BLK, 3)     # left, north of module
line([(38.8, 12), (38.8, 27)], RED, 3); line([(41.2, 10), (41.2, 27)], BLK, 3)       # left, a1/b1 row
line([(118.8, 12), (118.8, 133)], RED, 3); line([(121.2, 10), (121.2, 131)], BLK, 3)  # right
line([(118.8, 38.8), (56, 38.8)], RED, 3); line([(121.2, 41.2), (56, 41.2)], BLK, 3)  # link west
line([(56, 38.8), (56, 56), (38.8, 56)], RED, 3); line([(57.5, 41.2), (57.5, 57.5), (41.2, 57.5), (41.2, 56)], BLK, 3)
line([(24, 27), (38.8, 27)], RED, 2); line([(24, 27), (24, 56), (38.8, 56)], RED, 2)  # left spines joined round the module
line([(22.5, 27), (41.2, 27)], BLK, 2); line([(22.5, 27), (22.5, 57.5), (41.2, 57.5)], BLK, 2)

# ---- sensors ----
mcp_entry = {}
for i, sq in enumerate(squares):
    c, r = i % 4, i // 4
    cx, cy = SQ * (c + 0.5), SQ * (r + 0.5)
    rect(cx - 2.12, cy - 1.62, cx + 2.12, cy + 1.62, "#333", "#000")
    ly = cy - 2.4
    legs = {1: cx - 1.27, 2: cx, 3: cx + 1.27}
    for k, lx in legs.items():
        o.append(f'<circle cx="{X(lx):.1f}" cy="{Y(ly):.1f}" r="2.2" fill="{[None, RED, BLK, SIG][k]}" stroke="#000" stroke-width="0.5"/>')
    text(cx, cy + 5, sq, 14, "#000", bold=True)
    bx = 40 if cx < 80 else 120
    line([(legs[1], ly), (legs[1], ly - 3), (bx - 1.2, ly - 3)], RED, 1.6)
    line([(legs[2], ly), (legs[2], ly - 5), (bx + 1.2, ly - 5)], BLK, 1.6)
    sy = ly - 7 - 0.8 * c
    line([(legs[3], ly), (legs[3], sy)], SIG, 1.4)
    mcp_entry[sq] = (legs[3], sy, cx, cy)

# ---- signals: along the trunks (through the clips), then a short hop to the module's north edge ----
for sq, (lx, sy, cx, cy) in mcp_entry.items():
    i = squares.index(sq); tx = gp_x(sq)
    if cy < 40:                                   # a1, b1: round the module's side, up to the north edge
        side = 20 if cx < 40 else 60
        pts = [(lx, sy), (side, sy), (side, NORTH + 3 + 0.5 * i), (tx, NORTH + 3 + 0.5 * i), (tx, NORTH)]
    elif cx < 80 and cy < 80:                     # a2, b2: straight down onto the north edge
        pts = [(lx, sy), (tx, sy), (tx, NORTH)]
    elif cx < 80:                                 # a3-b4: into the x = 40 trunk, south to the module
        tr = 40 + (-0.6 if cx < 40 else 0.6) + 0.25 * (r := i // 4)
        pts = [(lx, sy), (tr, sy), (tr, NORTH + 4 + 0.4 * (i % 8)), (tx, NORTH + 4 + 0.4 * (i % 8)), (tx, NORTH)]
    else:                                         # c/d columns: x = 120 trunk, west along y = 40, hop north
        k = (i // 4) * 2 + (i % 4 - 2)            # 0..7
        tr = 119.2 + 0.25 * k
        ty = 39.0 + 0.25 * k
        pts = [(lx, sy), (tr, sy), (tr, ty), (60 + 0.4 * k, ty), (60 + 0.4 * k, NORTH + 1.5 + 0.3 * k), (tx, NORTH + 1.5 + 0.3 * k), (tx, NORTH)]
    line(pts, SIG, 1.2)

# module on top, with its two snap clips, and the wire clips
draw_clips()
rect(MX0, MY0, MX1, MY1, "#cfe8ff", "#1f77b4", 2)
for k, xk in enumerate(PIN_X):                     # pin rows
    for yy in (NORTH - 1.3, NORTH - 3.84, MY0 + 1.3):
        o.append(f'<circle cx="{X(xk):.1f}" cy="{Y(yy):.1f}" r="1.6" fill="white" stroke="#1f77b4" stroke-width="0.6"/>')
for xe in (MX0 - 0.6, MX1 + 0.6):
    rect(xe - 0.6, 38.5, xe + 0.6, 41.5, "#555", "#000")
text(40, 42.5, "MCP23017", 12, "#1f77b4", bold=True); text(40, 38.5, "CJMCU-2317  0x20", 9, "#1f77b4")
text(40, 34.5, "inputs: north edge  power/I2C: south", 8, "#1f77b4")

# ---- bus in: through the outer-wall notch at (40, 0) ----
line([(38.5, -8), (38.5, 12)], RED, 3); line([(41.5, -8), (41.5, 10)], BLK, 3)
# south edge single row, from the west end: A2 A1 A0 RESET SO CS SDA SCL GND VCC
# (it runs the opposite way to the north row, whose west end is VCC/GND, as on the module)
line([(43.5, -8), (43.5, 4), (PIN_X[9], 4), (PIN_X[9], MY0)], ORG, 2.2)     # VCC (+ RESET, 3V3)
line([(44.5, -8), (44.5, 6), (PIN_X[6], 6), (PIN_X[6], MY0)], BLU, 2.2)     # SDA
line([(45.5, -8), (45.5, 8), (PIN_X[7], 8), (PIN_X[7], MY0)], GRN, 2.2)     # SCL
text(41, -11, "BUS to Pico / next tile: 5V, GND, 3V3, SDA, SCL", 12, "#000", bold=True)

# ---- legend and notes (right column) ----
lx0, ly0 = M + SIZE * S + 30, M + 10
def leg(y, col, t, w=4):
    o.append(f'<line x1="{lx0}" y1="{y}" x2="{lx0+30}" y2="{y}" stroke="{col}" stroke-width="{w}"/>')
    text(lx0 + 38, y + 4, t, 12, anchor="start", raw=True)
text(lx0, ly0, "ONE TILE, SEEN FROM UNDERNEATH", 14, anchor="start", bold=True, raw=True)
text(lx0, ly0 + 18, "(flip the tile over: square a1 is now bottom-RIGHT)", 11, anchor="start", raw=True)
leg(ly0 + 45, RED, "+5V: sensor leg 1 (VS)")
leg(ly0 + 65, BLK, "GND: sensor leg 2, MCP GND, A0, A1, A2")
leg(ly0 + 85, SIG, "signal: sensor leg 3 (OUT) to its MCP pin", 2)
leg(ly0 + 105, ORG, "+3V3: MCP VCC and RESET")
leg(ly0 + 125, BLU, "SDA (Pico GP4, pin 6)")
leg(ly0 + 145, GRN, "SCL (Pico GP5, pin 7)")
text(lx0, ly0 + 180, "Legs from below (sensor face up):", 12, anchor="start", bold=True, raw=True)
for k, (col, name) in enumerate(((SIG, "3 OUT"), (BLK, "2 GND"), (RED, "1 VS"))):
    o.append(f'<circle cx="{lx0 + 20 + 55*k}" cy="{ly0 + 200}" r="7" fill="{col}" stroke="#000"/>')
    text(lx0 + 20 + 55 * k, ly0 + 222, name, 11, raw=True)
text(lx0, ly0 + 245, "Mirrored compared with the face view.", 11, anchor="start", raw=True)
text(lx0, ly0 + 275, "Square to MCP23017 pin:", 12, anchor="start", bold=True, raw=True)
for r in range(4, 0, -1):
    row = "   ".join(f"{f}{r}={pin_of[f + str(r)]}" for f in "abcd")
    text(lx0, ly0 + 295 + 17 * (4 - r), row, 11, anchor="start", raw=True)
notes = ["Rails: + and GND run down the middle of each bay",
         "and pass between bays through the notches.",
         "Signals: one wire per sensor to the MCP23017",
         "(ribbon cable works well, 4 wires per bay).",
         "MCP23017 snaps into 2 clips (grey marks), 5 mm",
         "below the deck. Inputs on its north edge.",
         "Brown pairs = wire clips: press the bundle in.",
         "Trunks: x=40, x=120 and y=40, through the notches.",
         "Pull-ups: 10k from each signal to 3V3, at the MCP end.",
         "Also: 100 nF across MCP VCC/GND, 10 uF across 5V/GND.",
         "Check each sensor's legs for shorts before power."]
for k, n in enumerate(notes):
    text(lx0, ly0 + 385 + 16 * k, n, 11, anchor="start", raw=True)
text(M, M + SIZE * S + 80, "Map to scale: 4 px per mm. Grey = tile walls and centre rib, white slots = wire notches, circles = M3 bolt holes.", 11, anchor="start", raw=True)
# ======================================================================================
# MODULE CLOSE-UP: every connection at the MCP23017, the Pico, the capacitors and the
# pull-up resistors. Build these connections; the map above shows where the wires run.
# ======================================================================================
T0 = M + SIZE * S + 150                     # top of the close-up section
Z = 14.0                                    # px per mm in the close-up
o.append(f'<line x1="{M}" y1="{T0 - 30}" x2="{W - M}" y2="{T0 - 30}" stroke="#999" stroke-width="1"/>')
text(M, T0 - 8, "MCP23017 CLOSE-UP (seen from underneath, label side facing you): build these connections exactly", 14, anchor="start", bold=True, raw=True)
mx0, my0 = M + 400, T0 + 250                # module top-left (px)
mw, mh = 26.7 * Z, 21.5 * Z
o.append(f'<rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" fill="#cfe8ff" stroke="#1f77b4" stroke-width="2"/>')
text(mx0 + mw / 2, my0 + mh / 2 + 5, "MCP23017 (CJMCU-2317)", 14, "#1f77b4", bold=True, raw=True)
px = lambda k: mx0 + mw / 2 + (k - 4.5) * 2.54 * Z
yo, yi, ys = my0 + 18, my0 + 18 + 2.54 * Z, my0 + mh - 18    # north outer, north inner, south rows
def hole(x, y): o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="white" stroke="#1f77b4" stroke-width="1.5"/>')
def seg(pts, col, w=2.2):
    o.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"/>')
def rtext(x, y, t, size=10, col="#000", ang=-90, bold=False):
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}"{" font-weight=\"bold\"" if bold else ""} transform="rotate({ang} {x:.1f} {y:.1f})">{t}</text>')

north = ["VCC/GND", "ITB/ITA"] + [f"B{n}/A{n}" for n in range(8)]
south = ["A2", "A1", "A0", "RESET", "NC/SO", "NC/CS", "SDA", "SCL", "GND", "VCC"]
for k in range(10):
    hole(px(k), yo); hole(px(k), yi); hole(px(k), ys)
    rtext(px(k) + 4, yi + 62, north[k], 10, "#1f77b4")
    rtext(px(k) + 4, ys - 12, south[k], 10, "#1f77b4")

# north edge: 16 inputs. Each pair = one A pin + one B pin. 10k from each pin up to the 3V3 bus,
# and the sensor wire solders to the same pin.
PB = my0 - 200
seg([(px(2) - 20, PB), (mx0 + mw + 45, PB)], ORG, 3)
for k in range(2, 10):
    n = k - 2
    for dx, row_y, port in ((-9, yo, "A"), (9, yi, "B")):
        x = px(k) + dx
        sq = squares[n] if port == "A" else squares[8 + n]
        seg([(x, PB), (x, PB + 10)], ORG, 1.6)
        o.append(f'<rect x="{x - 4:.1f}" y="{PB + 10:.1f}" width="8" height="26" fill="#f3e2c0" stroke="#000" stroke-width="1"/>')
        seg([(x, PB + 36), (x, row_y - 7)], SIG, 1.8)
        rtext(x + 5, my0 - 12, f"{sq} = GP{port}{n}", 10, "#7a5a00", bold=True)
text(px(2) - 26, PB + 4, "3V3 pull-up bus", 12, ORG, anchor="end", bold=True, raw=True)
text(px(2) - 26, PB + 28, "R1-R16: 10k each", 12, "#000", anchor="end", bold=True, raw=True)
text(px(2) - 26, PB + 44, "(one per input pin)", 11, "#000", anchor="end", raw=True)
text(px(0) - 12, PB + 110, "sensor wire for each square", 12, "#7a5a00", anchor="end", bold=True, raw=True)
text(px(0) - 12, PB + 126, "solders to the same pin", 11, "#7a5a00", anchor="end", raw=True)
text(px(0) - 12, PB + 142, "as its resistor", 11, "#7a5a00", anchor="end", raw=True)
rtext(px(0) + 4, yo - 12, "empty", 10, "#c00", bold=True)
rtext(px(1) + 4, yo - 12, "empty", 10, "#c00", bold=True)
text(px(0) - 12, yo + 4, "VCC/GND and ITB/ITA pairs: leave empty", 11, "#c00", anchor="end", bold=True, raw=True)

# south edge: power, I2C, address, reset. Short labelled stubs only, so no lines cross:
# every stub labelled GND joins the GND rail, every 3V3 stub joins 3V3.
BY = ys + 150
def stub(k, col, label, length=55, label_col=None):
    seg([(px(k), ys + 7), (px(k), ys + length)], col, 3)
    rtext(px(k) + 4, ys + length + 8 + 6 * len(label), label, 11, label_col or col, bold=True)
stub(0, BLK, "GND"); stub(1, BLK, "GND"); stub(2, BLK, "GND")
stub(3, ORG, "3V3")
for k in (4, 5):
    rtext(px(k) + 4, ys + 60, "empty", 10, "#c00", bold=True)
for k, col in ((6, BLU), (7, GRN), (8, BLK)):
    seg([(px(k), ys + 7), (px(k), BY)], col, 3)
seg([(px(9), ys + 7), (px(9), BY)], ORG, 3)
seg([(px(9), ys + 48), (mx0 + mw + 45, ys + 48), (mx0 + mw + 45, PB)], ORG, 3)  # VCC up to the pull-up bus
o.append(f'<circle cx="{px(9):.1f}" cy="{ys + 48:.1f}" r="4" fill="{ORG}"/>')
text(px(0) - 12, ys + 40, "A2, A1, A0 and RESET:", 11, anchor="end", bold=True, raw=True)
text(px(0) - 12, ys + 56, "short wires: A2-A0 to the GND rail,", 11, anchor="end", raw=True)
text(px(0) - 12, ys + 72, "RESET to the 3V3 bus (address 0x20)", 11, anchor="end", raw=True)
cx1 = (px(8) + px(9)) / 2                                                      # C1 across GND-VCC
seg([(px(8), ys + 28), (cx1 - 4, ys + 28)], BLK, 1.6); seg([(cx1 + 4, ys + 28), (px(9), ys + 28)], ORG, 1.6)
o.append(f'<line x1="{cx1 - 4}" y1="{ys + 18}" x2="{cx1 - 4}" y2="{ys + 38}" stroke="#000" stroke-width="3"/><line x1="{cx1 + 4}" y1="{ys + 18}" x2="{cx1 + 4}" y2="{ys + 38}" stroke="#000" stroke-width="3"/>')
text(mx0 + mw + 55, ys + 22, "C1 100nF across GND and VCC", 11, anchor="start", bold=True, raw=True)
text(mx0 + mw + 55, ys + 37, "(either way round)", 11, anchor="start", raw=True)
for x, t in ((px(6), "SDA"), (px(7), "SCL"), (px(8), "GND"), (px(9), "3V3")):
    rtext(x + 4, BY + 32, t, 10, "#000", bold=True)
text(mx0 + mw + 55, BY - 4, "these 4 + the 5V rail = the bus,", 11, anchor="start", raw=True)
text(mx0 + mw + 55, BY + 11, "out through the bus notch to the Pico", 11, anchor="start", raw=True)

# Pico box
pico_x, pico_y = M, BY + 60
o.append(f'<rect x="{pico_x}" y="{pico_y}" width="420" height="125" fill="#e9f7e9" stroke="#2ca02c" stroke-width="2"/>')
text(pico_x + 10, pico_y + 20, "Raspberry Pi Pico (powered by USB)", 13, "#185c18", anchor="start", bold=True, raw=True)
rows = [(RED, "VBUS     pin 40  ->  +5V rail (every sensor leg 1)"), (BLK, "GND      pin 38  ->  GND rail and MCP GND"),
        (ORG, "3V3(OUT) pin 36  ->  MCP VCC (3V3 only, never 5V)"), (BLU, "GP4      pin 6   ->  MCP SDA"), (GRN, "GP5      pin 7   ->  MCP SCL")]
for j, (col, t) in enumerate(rows):
    yy = pico_y + 42 + 18 * j
    o.append(f'<line x1="{pico_x + 10}" y1="{yy - 4}" x2="{pico_x + 34}" y2="{yy - 4}" stroke="{col}" stroke-width="5"/>')
    o.append(f'<text x="{pico_x + 42}" y="{yy}" font-size="12" font-family="monospace">{t}</text>')

# C2 electrolytic on the 5V rail
c2x, c2y = pico_x + 470, pico_y + 10
o.append(f'<line x1="{c2x}" y1="{c2y}" x2="{c2x + 60}" y2="{c2y}" stroke="{RED}" stroke-width="3"/><line x1="{c2x}" y1="{c2y + 60}" x2="{c2x + 60}" y2="{c2y + 60}" stroke="{BLK}" stroke-width="3"/>')
o.append(f'<rect x="{c2x + 18}" y="{c2y + 12}" width="24" height="36" rx="3" fill="#335" stroke="#000"/><rect x="{c2x + 18}" y="{c2y + 38}" width="24" height="10" fill="#ddd"/>')
o.append(f'<line x1="{c2x + 30}" y1="{c2y}" x2="{c2x + 30}" y2="{c2y + 12}" stroke="#000" stroke-width="2"/><line x1="{c2x + 30}" y1="{c2y + 48}" x2="{c2x + 30}" y2="{c2y + 60}" stroke="#000" stroke-width="2"/>')
text(c2x + 70, c2y + 4, "+5V rail", 12, RED, anchor="start", bold=True, raw=True)
text(c2x + 70, c2y + 24, "C2 10uF electrolytic, anywhere on the tile's rails", 12, anchor="start", raw=True)
text(c2x + 70, c2y + 40, "STRIPE (-) leg to GND. Backwards it can pop.", 12, "#c00", anchor="start", bold=True, raw=True)
text(c2x + 70, c2y + 64, "GND rail", 12, BLK, anchor="start", bold=True, raw=True)

# safe build order
steps = ["SAFE BUILD ORDER",
         "1. Before any power, multimeter on continuity: 5V-GND, 3V3-GND and 5V-3V3 must NOT beep. Each sensor: no beep between any two legs.",
         "2. Wire sensors + 5V/GND rails only, signal wires loose. Power the Pico. Measure each loose signal wire to GND: must NOT read 5 V.",
         "   A 5 V reading means that sensor's legs are wired wrong. Fix it before anything touches the MCP23017.",
         "3. Wire the module's south edge only (3V3, GND, SDA, SCL, RESET, A0-A2, C1). Run the tile test: it must find 0x20, all squares empty.",
         "4. Power off. Add the 16 pull-ups and the signal wires. Run the test again and try every square.",
         "Follow the LABELS printed on your module. If it's turned round, the positions here flip; the names don't."]
for j, t in enumerate(steps):
    text(M, pico_y + 175 + 19 * j, t, 13 if j == 0 else 12, "#c00" if j in (0, 6) else "#000", anchor="start", bold=(j in (0, 6)), raw=True)
o.append("</svg>")
open(OUT, "w").write("\n".join(o))
print("wrote", OUT)
