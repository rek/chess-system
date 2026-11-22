# Generates a to-scale wiring map of ONE sensor tile, seen from UNDERNEATH (where you solder).
# Run from the repo root:  python3 board/schematic/make_tile_wiring.py
# Writes board/schematic/tile_wiring.svg (open it in a browser).
# Dimensions follow board/case/sensor_tile.py; connections follow tile.kicad_sch.
import os

OUT = os.path.join("board", "schematic", "tile_wiring.svg")
S, M = 4.0, 40            # px per mm, margin px
SIZE, SQ = 160.0, 40.0
W, H = int(SIZE * S + 2 * M + 330), int(SIZE * S + 2 * M + 150)

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

# ---- power rails: a spine down the middle of each bay, joined through the notches ----
for bx in (40, 120):
    line([(bx - 1.5, 12), (bx - 1.5, 133)], RED, 3)      # 5V spine (through notch (bx, 80))
    line([(bx + 1.5, 10), (bx + 1.5, 131)], BLK, 3)      # GND spine
line([(38.5, 44), (118.5, 44)], RED, 3)                  # left-right link through notch (80, 40)
line([(41.5, 46), (121.5, 46)], BLK, 3)

# ---- sensors ----
mcp_entry = {}
for i, sq in enumerate(squares):
    c, r = i % 4, i // 4
    cx, cy = SQ * (c + 0.5), SQ * (r + 0.5)
    rect(cx - 2.12, cy - 1.62, cx + 2.12, cy + 1.62, "#333", "#000")           # sensor body (face up, seen from below)
    ly = cy - 2.4                                                               # legs come down through the slot
    legs = {1: cx - 1.27, 2: cx, 3: cx + 1.27}
    for k, lx in legs.items():
        o.append(f'<circle cx="{X(lx):.1f}" cy="{Y(ly):.1f}" r="2.2" fill="{[None, RED, BLK, SIG][k]}" stroke="#000" stroke-width="0.5"/>')
    text(cx, cy + 5, sq, 14, "#000", bold=True)
    bx = 40 if cx < 80 else 120
    line([(legs[1], ly), (legs[1], ly - 3), (bx - 1.5, ly - 3)], RED, 1.6)    # VS to the 5V spine
    line([(legs[2], ly), (legs[2], ly - 5), (bx + 1.5, ly - 5)], BLK, 1.6)    # GND to the GND spine
    sy = ly - 7 - 0.8 * c
    line([(legs[3], ly), (legs[3], sy)], SIG, 1.4)
    mcp_entry[sq] = (legs[3], sy, cx, cy)

# ---- signals: one wire per sensor to the MCP23017, crossing ribs only at the notches ----
top_k = right_k = 0
for sq, (lx, sy, cx, cy) in mcp_entry.items():
    if cx < 80 and cy < 40:                      # a1, b1: below the module, land on its bottom edge
        tx = MX1 - 4 + 2 * (cx > 40)
        pts = [(lx, sy), (tx, sy), (tx, MY0)]
    elif cx < 80 and cy < 80:                    # a2, b2: land on the top edge
        tx = MX0 + 3 + 2 * top_k; top_k += 1
        pts = [(lx, sy), (tx, sy), (tx, MY1)]
    elif cx < 80:                                # a3-b4: through notch (40, 80), x 43-46
        nx = 43 + 0.8 * top_k
        tx = MX0 + 3 + 2 * top_k; top_k += 1
        pts = [(lx, sy), (nx, sy), (nx, MY1 + 6 - 0.8 * top_k), (tx, MY1 + 6 - 0.8 * top_k), (tx, MY1)]
    else:                                        # right half: through notch (80, 40), y 34-40
        k = right_k; right_k += 1
        cyx = 35 + 0.6 * k                       # crossing height at the rib
        ty = MY0 + 1.2 + 1.1 * k                 # landing on the module's right edge
        cx_col = 84 + 0.8 * k
        if cy < 80:
            pts = [(lx, sy), (cx_col, sy), (cx_col, cyx), (73 - 0.3 * k, cyx), (73 - 0.3 * k, ty), (MX1, ty)]
        else:                                    # far bay: first through notch (120, 80), x 123-126
            nx = 123 + 0.4 * (k - 4)
            pts = [(lx, sy), (nx, sy), (nx, 70 - 0.8 * k), (cx_col, 70 - 0.8 * k), (cx_col, cyx), (73 - 0.3 * k, cyx), (73 - 0.3 * k, ty), (MX1, ty)]
    line(pts, SIG, 1.2)

# module on top, with its two snap clips
rect(MX0, MY0, MX1, MY1, "#cfe8ff", "#1f77b4", 2)
for xe in (MX0 - 0.6, MX1 + 0.6):
    rect(xe - 0.6, 38.5, xe + 0.6, 41.5, "#555", "#000")
text(40, 41.5, "MCP23017", 12, "#1f77b4", bold=True); text(40, 37.5, "CJMCU-2317  0x20", 9, "#1f77b4")
text(40, 33.5, "labels face you", 9, "#1f77b4")

# ---- bus in: through the outer-wall notch at (40, 0) ----
line([(38.5, -8), (38.5, 12)], RED, 3); line([(41.5, -8), (41.5, 10)], BLK, 3)
line([(43.5, -8), (43.5, 4), (48, 4), (48, MY0)], ORG, 2.2)
line([(44.5, -8), (44.5, 3), (50.5, 3), (50.5, MY0)], BLU, 2.2)
line([(45.5, -8), (45.5, 2), (53, 2), (53, MY0)], GRN, 2.2)
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
         "MCP23017 snaps into 2 clips (dark marks), 5 mm",
         "below the deck; wires can run under it.",
         "Also: 100 nF across MCP VCC/GND, 10 uF across 5V/GND.",
         "Check each sensor's legs for shorts before power."]
for k, n in enumerate(notes):
    text(lx0, ly0 + 385 + 16 * k, n, 11, anchor="start", raw=True)
text(M, H - 20, "To scale: 4 px per mm. Grey = tile walls and centre rib, white slots = wire notches, circles = M3 bolt holes.", 11, anchor="start", raw=True)
o.append("</svg>")
open(OUT, "w").write("\n".join(o))
print("wrote", OUT)
