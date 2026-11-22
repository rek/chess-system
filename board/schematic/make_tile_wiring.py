# Generates the wiring map of ONE sensor tile, seen from UNDERNEATH (where you solder).
# Run from the repo root:  python3 board/schematic/make_tile_wiring.py
# Writes board/schematic/tile_wiring.svg (open it in a browser). This is the build reference:
#   panel A: 5V + GND chain (sensor to sensor, joined on the legs) and the WAGO bus junction
#   panel B: one signal wire per sensor to the MCP23017
#   close-up: every connection at the MCP23017, the Pico, the capacitors, the pull-ups
# Dimensions follow board/case/sensor_tile.py; connections follow tile.kicad_sch.
import os

OUT = os.path.join("board", "schematic", "tile_wiring.svg")
S, M = 4.0, 40            # px per mm on the panels, page margin px
SIZE, SQ = 160.0, 40.0
PA, PB_X, PY = 80, 840, 150                # panel A x, panel B x, panels y (tile top-left, px)
W, H = int(PB_X + SIZE * S + 60), 2090
OX, OY = PA, PY
X = lambda x: OX + (SIZE - x) * S          # underside view: x mirrors, model +y up the page
Y = lambda y: OY + (SIZE - y) * S
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
    px_, py_ = (x, y) if raw else (X(x), Y(y))
    o.append(f'<text x="{px_:.1f}" y="{py_:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{" font-weight=\"bold\"" if bold else ""}>{t}</text>')

RED, BLK, SIG, ORG, BLU, GRN = "#d62728", "#222", "#e6a700", "#ff7f0e", "#1f77b4", "#2ca02c"
squares = [f + str(r) for r in range(1, 5) for f in "abcd"]
pin_of = {sq: ("GPA%d" % i if i < 8 else "GPB%d" % (i - 8)) for i, sq in enumerate(squares)}
MX0, MX1, MY0, MY1 = 26.65, 53.35, 29.25, 50.75                 # MCP23017 module outline
PIN_X = [40 + (k - 4.5) * 2.54 for k in range(10)]               # k = 0: VCC/GND end (west)
NORTH = MY1
def gp_x(sq):
    i = squares.index(sq); n = i % 8
    return PIN_X[n + 2] + (0.5 if i >= 8 else -0.5)
WIRE_CLIPS = ([(40, y, "y") for y in (72, 94, 106, 134)] +
              [(120, y, "y") for y in (26, 54, 66, 94, 106, 134)] +
              [(x, 40, "x") for x in (62, 72, 88, 100, 110)])
WAGO_X = {"5V": 99.9, "GND": 120.0, "3V3": 140.1, "SDA": 29.95, "SCL": 50.05}
WCOL = {"5V": RED, "GND": BLK, "3V3": ORG, "SDA": BLU, "SCL": GRN}
LEG = {}
for i, sq in enumerate(squares):
    c, r = i % 4, i // 4
    cx, cy = SQ * (c + 0.5), SQ * (r + 0.5)
    LEG[sq] = (cx, cy, cy - 2.4, {1: cx - 1.27, 2: cx, 3: cx + 1.27})

def base(title, sub):
    """tile structure, clips, WAGO slots, sensors and module: same on both panels"""
    text(X(160), Y(160) - 112, title, 15, anchor="start", bold=True, raw=True)
    text(X(160), Y(160) - 94, sub, 11, anchor="start", raw=True)
    rect(0, 0, SIZE, SIZE, "#f4f4f4", "#555", 2)
    rect(79.4, 0, 80.6, SIZE, "#bbb", "#888"); rect(0, 79.4, SIZE, 80.6, "#bbb", "#888")
    for k in (40, 120):
        for (x, y) in ((k, 0), (k, 80), (k, SIZE)):
            rect(k - 6, y - 1.5, k + 6, y + 1.5, "white", "#555")
        for (x, y) in ((0, k), (80, k), (SIZE, k)):
            rect(x - 1.5, k - 6, x + 1.5, k + 6, "white", "#555")
    for k in (20, 140):
        for (x, y) in ((k, 1.2), (k, SIZE - 1.2), (1.2, k), (SIZE - 1.2, k)):
            o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{1.7*S:.1f}" fill="white" stroke="#555"/>')
    for cx, cy, al in WIRE_CLIPS:
        for sd in (-1, 1):
            if al == "y":
                rect(cx + sd * 2.4 - 0.6, cy - 2, cx + sd * 2.4 + 0.6, cy + 2, "#7a4b00", "#3a2400")
            else:
                rect(cx - 2, cy + sd * 2.4 - 0.6, cx + 2, cy + sd * 2.4 + 0.6, "#7a4b00", "#3a2400")
    for nm, wx in WAGO_X.items():
        rect(wx - 9.4, 110.7, wx + 9.4, 129.3, "#fff1db", "#c47a00", 1.5)
        text(wx, 113, f"WAGO {nm}", 10, WCOL[nm], bold=True)
    rect(MX0, MY0, MX1, MY1, "#cfe8ff", "#1f77b4", 2)
    for xe in (MX0 - 0.6, MX1 + 0.6):
        rect(xe - 0.6, 38.5, xe + 0.6, 41.5, "#555", "#000")
    for xk in PIN_X:
        for yy in (NORTH - 1.3, NORTH - 3.84, MY0 + 1.3):
            o.append(f'<circle cx="{X(xk):.1f}" cy="{Y(yy):.1f}" r="1.6" fill="white" stroke="#1f77b4" stroke-width="0.6"/>')
    for xk in PIN_X[2:]:                                          # pull-ups, lying north of the module
        rect(xk - 1.2, 51.2, xk + 1.2, 57.7, "#f3e2c0", "#8a6d2b", 0.8)
    rect(24.5, 59, 55.5, 61, "#7a4b00", "#3a2400")               # pull-up comb
    o.append(f'<line x1="{X(28.5):.1f}" y1="{Y(63):.1f}" x2="{X(52.5):.1f}" y2="{Y(63):.1f}" stroke="{ORG}" stroke-width="2.5"/>')
    text(40, 65.5, "pull-up comb + 3V3 wire", 9, "#7a4b00", bold=True)
    text(40, 41, "MCP23017", 12, "#1f77b4", bold=True)
    text(40, 36.5, "inputs: north edge", 9, "#1f77b4"); text(40, 33, "power / I2C: south edge", 9, "#1f77b4")
    for sq, (cx, cy, ly, legs) in LEG.items():
        rect(cx - 2.12, cy - 1.62, cx + 2.12, cy + 1.62, "#333", "#000")
        text(cx, cy + 5, sq, 14, "#000", bold=True)
def leg_dots(which):
    for sq, (cx, cy, ly, legs) in LEG.items():
        for k, lx in legs.items():
            col = [None, RED, BLK, SIG][k] if k in which else "#ddd"
            o.append(f'<circle cx="{X(lx):.1f}" cy="{Y(ly):.1f}" r="2.3" fill="{col}" stroke="#000" stroke-width="0.5"/>')

# ====================================== PANEL A: power ======================================
OX, OY = PA, PY
base("A. POWER: 5V + GND chain and the WAGO bus junction",
     "5V (leg 1) and GND (leg 2) run sensor to sensor: solder the wire in and the wire out onto the same leg.")
CHAIN = ["d4", "c4", "c3", "d3", "N120_80", "d2", "d1", "c1", "c2", "N80_40",
         "b2", "b1", "a1", "a2", "N40_80", "a3", "a4", "b4", "b3"]
COL_SIDE = {"a": -6, "b": 6, "c": -6, "d": -6}
def hop(s1, s2, notch, wi):
    cx1, cy1, ly1, l1 = LEG[s1]; cx2, cy2, ly2, l2 = LEG[s2]
    k = 1 + wi
    y1, y2 = ly1 - 3 - 2 * wi, ly2 - 3 - 2 * wi
    if notch == "N120_80":
        nx = 122 + 1.5 * wi
        return [(l1[k], ly1), (l1[k], y1), (nx, y1), (nx, y2), (l2[k], y2), (l2[k], ly2)]
    if notch == "N80_40":
        ny = 44 + 1.5 * wi
        return [(l1[k], ly1), (l1[k], ny), (l2[k] + 4 + 1.5 * wi, ny), (l2[k] + 4 + 1.5 * wi, y2), (l2[k], y2), (l2[k], ly2)]
    if notch == "N40_80":
        nx = 36 - 1.5 * wi
        return [(l1[k], ly1), (l1[k], y1), (nx, y1), (nx, y2), (l2[k], y2), (l2[k], ly2)]
    if cy1 == cy2:
        return [(l1[k], ly1), (l1[k], y1), (l2[k], y2), (l2[k], ly2)]
    side = COL_SIDE[s1[0]]
    vx = cx1 + side + (1.5 * wi if side > 0 else -1.5 * wi)
    return [(l1[k], ly1), (l1[k], y1), (vx, y1), (vx, y2), (l2[k], y2), (l2[k], ly2)]
for wi, col in ((0, RED), (1, BLK)):
    j = 0
    while j < len(CHAIN) - 1:
        s1, nxt = CHAIN[j], CHAIN[j + 1]
        if nxt.startswith("N"):
            line(hop(s1, CHAIN[j + 2], nxt, wi), col, 2); j += 2
        else:
            line(hop(s1, nxt, None, wi), col, 2); j += 1
# bus in (north-wall notch at x = 120) to each WAGO, and out (east-wall notch at y = 120)
for j, nm in enumerate(("5V", "GND", "3V3", "SDA", "SCL")):
    xin, wx, col = 115.5 + 2.2 * j, WAGO_X[nm], WCOL[nm]
    if nm in ("SDA", "SCL"):           # to the a3-b4 bay through the centre-rib notch at y = 120
        line([(xin, 170), (xin, 156 - 1.5 * j), (84 + 1.5 * (j - 3), 156 - 1.5 * j), (84 + 1.5 * (j - 3), 124 + 1.5 * (j - 3)), (wx + 3, 124 + 1.5 * (j - 3)), (wx + 3, 129.3)], col, 2)
        line([(wx - 3, 129.3), (wx - 3, 107 - 1.5 * (j - 3)), (76, 107 - 1.5 * (j - 3)), (76, 116 + 1.5 * (j - 3)), (156 + 1.5 * (j - 3), 116 + 1.5 * (j - 3)), (170, 116 + 1.5 * (j - 3))], col, 1.6, "5,3")
    else:
        line([(xin, 170), (xin, 133 + 1.5 * j), (wx + 3, 133 + 1.5 * j), (wx + 3, 129.3)], col, 2)
        line([(wx - 3, 129.3), (wx - 3, 106 - 1.5 * j), (158 - 1.5 * j, 106 - 1.5 * j), (158 - 1.5 * j, 120 + 1.5 * j), (170, 120 + 1.5 * j)], col, 1.6, "5,3")
text(120, 174, "BUS IN  (from the Pico / previous tile)", 12, "#000", bold=True)
o.append(f'<text x="{X(172):.1f}" y="{Y(120):.1f}" font-size="12" font-weight="bold" text-anchor="middle" transform="rotate(-90 {X(172):.1f} {Y(120):.1f})">BUS OUT (dashed, to next tile)</text>')
# taps: WAGO 5V/GND -> chain start d4; 3V3 -> module VCC; SDA/SCL -> module; GND -> module from b1
d4x, d4y, d4ly, d4l = LEG["d4"]
line([(WAGO_X["5V"], 129.3), (WAGO_X["5V"], 131), (d4l[1] - 5, 131), (d4l[1] - 5, d4ly - 3), (d4l[1], d4ly - 3), (d4l[1], d4ly)], RED, 2.6)
line([(WAGO_X["GND"], 129.3), (WAGO_X["GND"], 130), (d4l[2] - 3.5, 130), (d4l[2] - 3.5, d4ly - 5), (d4l[2], d4ly - 5), (d4l[2], d4ly)], BLK, 2.6)
line([(WAGO_X["3V3"], 129.3), (WAGO_X["3V3"], 103), (124.5, 103), (124.5, 36), (56.5, 36), (56.5, 24), (PIN_X[9], 24), (PIN_X[9], MY0)], ORG, 2.2)
line([(WAGO_X["SDA"], 129.3), (WAGO_X["SDA"], 104), (42.5, 104), (42.5, 58.5), (24, 58.5), (24, 25.5), (PIN_X[6], 25.5), (PIN_X[6], MY0)], BLU, 2.2)
line([(WAGO_X["SCL"], 129.3), (WAGO_X["SCL"], 102.5), (44, 102.5), (44, 57), (25.5, 57), (25.5, 27), (PIN_X[7], 27), (PIN_X[7], MY0)], GRN, 2.2)
for nm, wx in WAGO_X.items():                 # entry dots: every wire enters the north face
    for dx in (-3, 0, 3):
        o.append(f'<circle cx="{X(wx + dx):.1f}" cy="{Y(129.3):.1f}" r="3" fill="#c47a00"/>')
# 3V3 jumper: module VCC up to the pull-up comb's 3V3 wire
line([(PIN_X[9], MY0), (PIN_X[9], 28), (55.8, 28), (55.8, 63), (52.5, 63)], ORG, 2.2)
text(57.5, 45, "VCC to comb 3V3", 8, ORG, anchor="end", bold=True)
b1x, b1y, b1ly, b1l = LEG["b1"]
line([(b1l[2], b1ly), (b1l[2], b1ly - 9), (PIN_X[8], b1ly - 9), (PIN_X[8], MY0)], BLK, 2.2)
leg_dots((1, 2))
text(d4x + 8, d4ly - 9, "chain START (+ C2 here)", 10, "#c00", anchor="start", bold=True)
text(LEG["b3"][0] + 8, LEG["b3"][2] - 9, "chain END", 10, "#c00", anchor="start", bold=True)
text(b1x - 3, b1ly - 12, "module GND from b1's GND leg", 9, "#000", anchor="end")

# ====================================== PANEL B: signals ======================================
OX, OY = PB_X, PY
base("B. SIGNALS: one wire from each sensor's leg 3 to the MCP23017",
     "Each wire goes along a clip trunk, through the notches, to its pin on the module's north edge.")
for sq, (cx, cy, ly, legs) in LEG.items():
    i = squares.index(sq); c = i % 4
    lx = legs[3]; sy = ly - 7 - 0.8 * c; tx = gp_x(sq)
    if cy < 40:
        side = 20 if cx < 40 else 60
        pts = [(lx, ly), (lx, sy), (side, sy), (side, NORTH + 3 + 0.5 * i), (tx, NORTH + 3 + 0.5 * i), (tx, NORTH)]
    elif cx < 80 and cy < 80:
        pts = [(lx, ly), (lx, sy), (tx, sy), (tx, NORTH)]
    elif cx < 80:
        tr = 40 + (-0.6 if cx < 40 else 0.6) + 0.25 * (i // 4)
        pts = [(lx, ly), (lx, sy), (tr, sy), (tr, NORTH + 4 + 0.4 * (i % 8)), (tx, NORTH + 4 + 0.4 * (i % 8)), (tx, NORTH)]
    else:
        k = (i // 4) * 2 + (i % 4 - 2)
        tr, ty = 119.2 + 0.25 * k, 39.0 + 0.25 * k
        pts = [(lx, ly), (lx, sy), (tr, sy), (tr, ty), (60 + 0.4 * k, ty), (60 + 0.4 * k, NORTH + 1.5 + 0.3 * k), (tx, NORTH + 1.5 + 0.3 * k), (tx, NORTH)]
    line(pts, SIG, 1.6)
    text(cx + 3.2, cy - 1, pin_of[sq], 10, "#7a5a00", anchor="end", bold=True)
leg_dots((3,))

# ====================================== legend ======================================
LY = PY + SIZE * S + 40
def legend_line(x, y, col, t, w=5, dash=None):
    o.append(f'<line x1="{x}" y1="{y}" x2="{x+30}" y2="{y}" stroke="{col}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
    text(x + 38, y + 4, t, 12, anchor="start", raw=True)
legend_line(M, LY, RED, "+5V: sensor leg 1")
legend_line(M, LY + 20, BLK, "GND: sensor leg 2")
legend_line(M, LY + 40, SIG, "signal: sensor leg 3", 3)
legend_line(M + 260, LY, ORG, "+3V3 (MCP VCC, RESET, pull-ups)")
legend_line(M + 260, LY + 20, BLU, "SDA")
legend_line(M + 260, LY + 40, GRN, "SCL")
legend_line(M + 260, LY + 60, "#555", "dashed = bus OUT to the next tile", 2, "5,3")
text(M + 600, LY + 4, "Legs from below (sensor face up):", 12, anchor="start", bold=True, raw=True)
for k, (col, name) in enumerate(((SIG, "3 OUT"), (BLK, "2 GND"), (RED, "1 VS"))):
    o.append(f'<circle cx="{M + 620 + 60*k}" cy="{LY + 24}" r="8" fill="{col}" stroke="#000"/>')
    text(M + 620 + 60 * k, LY + 48, name, 11, raw=True)
text(M + 600, LY + 70, "Mirrored compared with the face view. Square a1 is bottom-RIGHT from below.", 11, anchor="start", raw=True)
text(M + 1000, LY + 4, "Brown pairs = wire clips (press the bundle in).", 11, anchor="start", raw=True)
text(M + 1000, LY + 20, "Orange boxes = WAGO 221-413, levers face you, slots (dots) face north.", 11, anchor="start", raw=True)
text(M + 1000, LY + 36, "Grey marks at the module = its snap clips.", 11, anchor="start", raw=True)
text(M + 1000, LY + 52, "Lines across a WAGO pass over it (between it and the deck).", 11, anchor="start", raw=True)
text(M + 1000, LY + 68, "Map to scale: 4 px per mm.", 11, anchor="start", raw=True)

# ======================================================================================
# MODULE CLOSE-UP: every connection at the MCP23017, the Pico, the capacitors and the
# pull-up resistors. Build these connections; the map above shows where the wires run.
# ======================================================================================
T0 = PY + SIZE * S + 190                    # top of the close-up section
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
        seg([(x, PB - 4), (x, PB + 34)], "#777", 1.4)
        o.append(f'<rect x="{x - 4:.1f}" y="{PB + 34:.1f}" width="8" height="32" fill="#f3e2c0" stroke="#000" stroke-width="1"/>')
        seg([(x, PB + 66), (x, row_y - 7)], "#777", 1.4)
        rtext(x + 5, my0 - 12, f"{sq} = GP{port}{n}", 10, "#7a5a00", bold=True)
o.append(f'<rect x="{px(0) - 16:.1f}" y="{PB + 10:.1f}" width="{px(9) - px(0) + 32:.1f}" height="14" fill="#7a4b00" stroke="#3a2400"/>')
for k in range(10):
    o.append(f'<rect x="{px(k) - 9 - 3:.1f}" y="{PB + 10:.1f}" width="24" height="9" fill="#fff" stroke="#3a2400" stroke-width="0.6"/>')
text(px(0) - 26, PB + 4, "bare 3V3 wire soldered along the legs", 12, ORG, anchor="end", bold=True, raw=True)
text(px(0) - 26, PB + 22, "pull-up comb (part of the tile)", 12, "#7a4b00", anchor="end", bold=True, raw=True)
text(px(0) - 26, PB + 50, "R1-R16: 10k each, one per input pin", 12, "#000", anchor="end", bold=True, raw=True)
text(px(0) - 26, PB + 66, "bend them as in the side view", 11, "#000", anchor="end", raw=True)
text(px(0) - 12, PB + 110, "sensor wire for each square goes into", 12, "#7a5a00", anchor="end", bold=True, raw=True)
text(px(0) - 12, PB + 126, "the same hole as its resistor, from", 11, "#7a5a00", anchor="end", raw=True)
text(px(0) - 12, PB + 142, "the other side (deck side)", 11, "#7a5a00", anchor="end", raw=True)
rtext(px(0) + 4, yo - 12, "empty", 10, "#c00", bold=True)
rtext(px(1) + 4, yo - 12, "empty", 10, "#c00", bold=True)
text(px(0) - 24, yo + 4, "VCC/GND and ITB/ITA pairs: leave empty", 11, "#c00", anchor="end", bold=True, raw=True)

# side view of the pull-ups (tile upside down on the bench: deck at the bottom)
Q, sx0, sy0 = 13.0, mx0 + mw + 200, T0 + 60
SX = lambda y: sx0 + (y - 42) * Q
SZ = lambda z: sy0 + z * Q
text(sx0 - 120, sy0 - 34, "SIDE VIEW of the pull-ups, from the east (tile upside down)", 13, anchor="start", bold=True, raw=True)
o.append(f'<rect x="{SX(42):.1f}" y="{SZ(17.6):.1f}" width="{26 * Q:.1f}" height="{2.4 * Q:.1f}" fill="#ccc" stroke="#555"/>')
o.append(f'<rect x="{SX(42):.1f}" y="{SZ(11):.1f}" width="{8.75 * Q:.1f}" height="{1.6 * Q:.1f}" fill="#cfe8ff" stroke="#1f77b4" stroke-width="1.5"/>')
o.append(f'<rect x="{SX(59):.1f}" y="{SZ(4):.1f}" width="{2 * Q:.1f}" height="{9 * Q:.1f}" fill="#7a4b00" fill-opacity="0.35" stroke="#3a2400"/>')
for yh, zl, nm in ((49.45, 10.2, "outer row: 1 mm off"), (46.91, 7.0, "inner row: 4 mm off")):
    seg([(SX(yh), SZ(13.2)), (SX(yh), SZ(zl)), (SX(65), SZ(zl))], "#777", 2)
    o.append(f'<rect x="{SX(51.2):.1f}" y="{SZ(zl - 1.25):.1f}" width="{6.5 * Q:.1f}" height="{2.5 * Q:.1f}" rx="6" fill="#f3e2c0" stroke="#000"/>')
    o.append(f'<circle cx="{SX(63.3):.1f}" cy="{SZ(zl):.1f}" r="4" fill="{ORG}"/>')
    text(SX(66), SZ(zl) + 4, nm, 11, anchor="start", raw=True)
seg([(SX(42), SZ(15.6)), (SX(46.3), SZ(15.6)), (SX(46.91), SZ(12.6))], SIG, 2.4)
text(SX(42) - 8, SZ(18.8) + 4, "deck", 11, "#555", anchor="end", raw=True)
text(SX(42) - 8, SZ(11.8) + 4, "module, label up", 11, "#1f77b4", anchor="end", bold=True, raw=True)
text(SX(42) - 8, SZ(15.6) + 4, "sensor wire", 11, "#7a5a00", anchor="end", raw=True)
text(SX(60), SZ(4) - 8, "comb", 11, "#7a4b00", anchor="middle", bold=True, raw=True)
text(SX(63.3), SZ(2) - 6, "3V3 wire", 11, ORG, anchor="middle", bold=True, raw=True)
text(sx0 - 120, SZ(20) + 26, "Bend each resistor's leg this far from the board before soldering it in.", 11, anchor="start", raw=True)
text(sx0 - 120, SZ(20) + 42, "Solder the resistors in before clipping the module in. Pushing it in drops", 11, anchor="start", raw=True)
text(sx0 - 120, SZ(20) + 58, "the far legs into the comb's slots; then solder the 3V3 wire along them.", 11, anchor="start", raw=True)

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
for x, t in ((px(6), "SDA: from WAGO SDA"), (px(7), "SCL: from WAGO SCL"), (px(8), "GND: from b1 leg 2"), (px(9), "3V3: from WAGO 3V3")):
    rtext(x + 4, BY + 112, t, 10, "#000", bold=True)
text(mx0 + mw + 55, BY - 4, "routes: see panel A", 11, anchor="start", raw=True)

# Pico box
pico_x, pico_y = M, BY + 60
o.append(f'<rect x="{pico_x}" y="{pico_y}" width="420" height="125" fill="#e9f7e9" stroke="#2ca02c" stroke-width="2"/>')
text(pico_x + 10, pico_y + 20, "Pico (on USB) -> the WAGOs' free 'in' slot", 13, "#185c18", anchor="start", bold=True, raw=True)
rows = [(RED, "VBUS     pin 40  ->  WAGO 5V"), (BLK, "GND      pin 38  ->  WAGO GND"),
        (ORG, "3V3(OUT) pin 36  ->  WAGO 3V3 (never 5V)"), (BLU, "GP4      pin 6   ->  WAGO SDA"), (GRN, "GP5      pin 7   ->  WAGO SCL")]
for j, (col, t) in enumerate(rows):
    yy = pico_y + 42 + 18 * j
    o.append(f'<line x1="{pico_x + 10}" y1="{yy - 4}" x2="{pico_x + 34}" y2="{yy - 4}" stroke="{col}" stroke-width="5"/>')
    o.append(f'<text x="{pico_x + 42}" y="{yy}" font-size="12" font-family="monospace">{t}</text>')

# C2 electrolytic on the 5V rail
c2x, c2y = mx0 + mw + 90, pico_y - 20
o.append(f'<line x1="{c2x}" y1="{c2y}" x2="{c2x + 60}" y2="{c2y}" stroke="{RED}" stroke-width="3"/><line x1="{c2x}" y1="{c2y + 60}" x2="{c2x + 60}" y2="{c2y + 60}" stroke="{BLK}" stroke-width="3"/>')
o.append(f'<rect x="{c2x + 18}" y="{c2y + 12}" width="24" height="36" rx="3" fill="#335" stroke="#000"/><rect x="{c2x + 18}" y="{c2y + 38}" width="24" height="10" fill="#ddd"/>')
o.append(f'<line x1="{c2x + 30}" y1="{c2y}" x2="{c2x + 30}" y2="{c2y + 12}" stroke="#000" stroke-width="2"/><line x1="{c2x + 30}" y1="{c2y + 48}" x2="{c2x + 30}" y2="{c2y + 60}" stroke="#000" stroke-width="2"/>')
text(c2x + 70, c2y + 4, "+5V rail", 12, RED, anchor="start", bold=True, raw=True)
text(c2x + 70, c2y + 24, "C2 10uF electrolytic, on legs 1 and 2 of d4 (chain start)", 12, anchor="start", raw=True)
text(c2x + 70, c2y + 40, "STRIPE (-) leg to GND. Backwards it can pop.", 12, "#c00", anchor="start", bold=True, raw=True)
text(c2x + 70, c2y + 64, "GND rail", 12, BLK, anchor="start", bold=True, raw=True)

# safe build order
steps = ["SAFE BUILD ORDER",
         "1. Before any power, multimeter on continuity: 5V-GND, 3V3-GND and 5V-3V3 must NOT beep. Each sensor: no beep between any two legs.",
         "2. Wire sensors + the 5V/GND chain + WAGOs only, signal wires loose. Power the Pico. Measure each loose signal wire to GND: must NOT read 5 V.",
         "   A 5 V reading means that sensor's legs are wired wrong. Fix it before anything touches the MCP23017.",
         "3. Wire the module's south edge only (3V3, GND, SDA, SCL, RESET, A0-A2, C1). Run the tile test: it must find 0x20, all squares empty.",
         "4. Power off. Unclip the module, solder the 16 pull-ups + signal wires, clip it back (legs into the comb), solder the comb's 3V3 wire + VCC jumper. Test every square.",
         "Follow the LABELS printed on your module. If it's turned round, the positions here flip; the names don't."]
for j, t in enumerate(steps):
    text(M, pico_y + 175 + 19 * j, t, 13 if j == 0 else 12, "#c00" if j in (0, 6) else "#000", anchor="start", bold=(j in (0, 6)), raw=True)
o.append("</svg>")
open(OUT, "w").write("\n".join(o))
print("wrote", OUT)
