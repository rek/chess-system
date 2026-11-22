# Sensor holder tile for the board underside (FreeCAD script).
# Run from the repo root:  freecadcmd board/case/sensor_tile.py
# Writes board/case/models/sensor_tile.step (+ .stl). Print 4, all identical.
# Also writes sensor_tile_coupon: one corner square, a quick print to check the sensor fit.
#
# One tile = 4 x 4 squares (160 x 160 mm) = 16 SS443R sensors = one MCP23017.
# Print it upside down (deck on the bed): the deck top comes out flat for the 3 mm sheet,
# and nothing needs supports.
#
#   deck (2.4 mm) with a pocket at every square centre: sensor face up, flush with the top
#   lead slot beside each pocket: bend the 3 leads straight down through it
#   perimeter walls + one cross rib, 20 mm deep: 4 open bays underneath for wiring,
#     the MCP23017 module and (on one tile) the Pico
#   wall holes (on 2.4 mm pads, at 20/140 mm): M3 bolts join neighbouring tiles (same holes on all 4 sides, so the tile
#     works in any corner, rotated)
#   notches at the deck side of walls and ribs: wires pass between bays and tiles
#   wire clips along 3 trunk routes (see WIRE_CLIPS) hold the wiring against the deck
#   two snap clips in the a1-b2 bay hold the MCP23017 module (CJMCU-2317)
import os
import FreeCAD as App, Part, Mesh, MeshPart
V = App.Vector

SQUARE   = 40.0           # chess square
N        = 4              # squares per side per tile
SIZE     = SQUARE * N     # 160 mm
HEIGHT   = 20.0           # total tile height (deck + bays)
DECK     = 2.4            # deck thickness (1.6 mm pocket + 0.8 mm floor)
WALL     = 1.2            # perimeter wall, 3 lines of a 0.4 mm nozzle
RIB      = 1.2            # cross rib at the tile centre lines
PAD_W, PAD_T = 8.0, 1.2   # full-height pad inside the wall at each bolt: 2.4 mm there

SENSOR_W, SENSOR_H, SENSOR_T = 4.1, 3.1, 1.6   # measured body: width, height (lead axis), thickness
CLEAR    = 0.07           # per side; 0.15 printed ~0.1-0.2 mm loose
SLOT_W, SLOT_D = SENSOR_W + 2 * CLEAR, 1.5     # lead slot, beside the lead edge of the pocket
# Deck windows: the deck is a lattice, not a solid plate (it was ~70 % of the plastic).
# Each square keeps a cross of arms through the sensor and a band along its edges;
# 4 windows per square are cut out. The 3 mm sheet on top spans the windows easily.
ARM      = 8.0            # width of the cross arms through the sensor
BAND     = 3.0            # solid band along each square edge (6 mm where two squares meet)

BOLT_D   = 3.4            # M3 clearance
BOLT_Z   = 10.0           # bolt height above the bottom edge
BOLT_AT  = (SQUARE / 2, SIZE - SQUARE / 2)   # 20 and 140 mm along each side, clear of the notches
NOTCH_W, NOTCH_H = 12.0, 8.0   # wire notch in walls/ribs, right under the deck (12 mm bridge in print)

# Wire clips: pairs of flexible posts hanging from the deck, forming a channel the wires
# press into. They sit on the solid deck bands along square edges, on 3 trunks:
#   x = 40 (a/b columns, rows 3-4, down to the module), x = 120 (c/d columns, through the
#   y = 80 rib), y = 40 (from x = 120 through the x = 80 rib towards the module).
CLIP_G, CLIP_PW, CLIP_L, CLIP_H = 3.6, 1.2, 4.0, 9.0   # channel width, post thickness, length, depth
CLIP_LIP = 1.3                                          # lips leave a 1.0 mm gap: wires snap past
WIRE_CLIPS = ([(40, y, "y") for y in (62, 94, 106, 134)] +
              [(120, y, "y") for y in (26, 54, 66, 94, 106, 134)] +
              [(x, 40, "x") for x in (62, 72, 88, 100, 110)])

# MCP23017 module (CJMCU-2317, 26.7 x 21.5 mm, no mounting holes) snaps in under the deck,
# centred in the a1-b2 bay, long side along x. Pins run along both long edges, so it is held
# only at the middle of its two short edges: a flexible arm with a hook, plus two small stops
# that set the gap to the deck. These sit on the solid deck band along y = 40.
MOD_X, MOD_Y = 26.7, 21.5     # module size
MOD_C    = (40.0, 40.0)       # centre (tile coordinates, a1 corner = 0,0)
MOD_GAP  = 5.0                # deck underside to module face (room for chip / solder joints)
PCB_T    = 1.6
ARM_W, ARM_T = 3.0, 1.0       # snap arm width (y) and thickness (x)
HOOK     = 0.5                # how far the hook reaches over the board edge
STOP_IN  = 1.0                # stops touch the board only this far in from its edge

OUT = os.path.join(os.getcwd(), "board", "case", "models")

def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))

# z = 0 is the bottom (table side), z = HEIGHT is the deck top (under the 3 mm sheet)
deck_z = HEIGHT - DECK
tile = box(0, 0, deck_z, SIZE, SIZE, DECK)
walls = [box(0, 0, 0, SIZE, WALL, deck_z), box(0, SIZE - WALL, 0, SIZE, WALL, deck_z),
         box(0, 0, 0, WALL, SIZE, deck_z), box(SIZE - WALL, 0, 0, WALL, SIZE, deck_z),
         box(SIZE / 2 - RIB / 2, 0, 0, RIB, SIZE, deck_z),
         box(0, SIZE / 2 - RIB / 2, 0, SIZE, RIB, deck_z)]
for k in BOLT_AT:   # bolt pads, full height so they print without overhangs
    walls += [box(k - PAD_W / 2, WALL, 0, PAD_W, PAD_T, deck_z),
              box(k - PAD_W / 2, SIZE - WALL - PAD_T, 0, PAD_W, PAD_T, deck_z),
              box(WALL, k - PAD_W / 2, 0, PAD_T, PAD_W, deck_z),
              box(SIZE - WALL - PAD_T, k - PAD_W / 2, 0, PAD_T, PAD_W, deck_z)]
# module clips: for each short edge, an arm + hook and two stops either side of it
def hook(xe, inward):
    zb = deck_z - MOD_GAP - PCB_T - 0.15            # just below the module's far face
    pts = [V(xe, MOD_C[1] - ARM_W / 2, zb), V(xe + inward * HOOK, MOD_C[1] - ARM_W / 2, zb),
           V(xe, MOD_C[1] - ARM_W / 2, zb - 1.5), V(xe, MOD_C[1] - ARM_W / 2, zb)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, ARM_W, 0))
for side in (-1, 1):
    xe = MOD_C[0] + side * (MOD_X / 2 + 0.15)       # board edge + clearance
    inward = -side
    zb = deck_z - MOD_GAP - PCB_T - 0.15
    arm_x0 = xe if side > 0 else xe - ARM_T
    walls.append(box(arm_x0, MOD_C[1] - ARM_W / 2, zb - 1.5, ARM_T, ARM_W, deck_z - (zb - 1.5)))
    walls.append(hook(xe, inward))
    sx0 = xe - STOP_IN - 0.15 if side > 0 else xe
    for y0 in (MOD_C[1] - ARM_W / 2 - 0.3 - 1.4, MOD_C[1] + ARM_W / 2 + 0.3):
        walls.append(box(sx0, y0, deck_z - MOD_GAP, STOP_IN + 0.15, 1.4, MOD_GAP))
def wire_clip(cx, cy, along):
    """Two posts either side of a channel running along `along`, lips at the free end."""
    parts = []
    zt = deck_z - CLIP_H
    for side in (-1, 1):
        off = side * (CLIP_G / 2 + CLIP_PW / 2)       # post centre, across the channel
        # post
        if along == "y":
            parts.append(box(cx + off - CLIP_PW / 2, cy - CLIP_L / 2, zt, CLIP_PW, CLIP_L, CLIP_H))
        else:
            parts.append(box(cx - CLIP_L / 2, cy + off - CLIP_PW / 2, zt, CLIP_L, CLIP_PW, CLIP_H))
        # lip: triangle in the cross-section, flat side up (holds wires), sloped side down
        inner = side * CLIP_G / 2                     # inner face of this post
        tip = inner - side * CLIP_LIP
        if along == "y":
            pts = [V(cx + inner, cy - CLIP_L / 2, zt + 1.6), V(cx + tip, cy - CLIP_L / 2, zt + 1.6),
                   V(cx + inner, cy - CLIP_L / 2, zt), V(cx + inner, cy - CLIP_L / 2, zt + 1.6)]
            parts.append(Part.Face(Part.makePolygon(pts)).extrude(V(0, CLIP_L, 0)))
        else:
            pts = [V(cx - CLIP_L / 2, cy + inner, zt + 1.6), V(cx - CLIP_L / 2, cy + tip, zt + 1.6),
                   V(cx - CLIP_L / 2, cy + inner, zt), V(cx - CLIP_L / 2, cy + inner, zt + 1.6)]
            parts.append(Part.Face(Part.makePolygon(pts)).extrude(V(CLIP_L, 0, 0)))
    return parts
for cx, cy, along in WIRE_CLIPS:
    walls += wire_clip(cx, cy, along)
tile = tile.fuse(walls)

cuts = []
pw, ph = SENSOR_W + 2 * CLEAR, SENSOR_H + 2 * CLEAR
for i in range(N):
    for j in range(N):
        cx, cy = SQUARE * (i + 0.5), SQUARE * (j + 0.5)
        # pocket: sensor face flush with the deck top
        cuts.append(box(cx - pw / 2, cy - ph / 2, HEIGHT - SENSOR_T, pw, ph, SENSOR_T + 1))
        # lead slot right below the pocket's lead edge (-y side), through the deck
        cuts.append(box(cx - SLOT_W / 2, cy - ph / 2 - SLOT_D + 0.01, deck_z - 1, SLOT_W, SLOT_D, DECK + 2))
        # 4 deck windows around the cross
        win = SQUARE / 2 - ARM / 2 - BAND
        for sx in (-1, 1):
            for sy in (-1, 1):
                x0 = cx + ARM / 2 if sx > 0 else cx - ARM / 2 - win
                y0 = cy + ARM / 2 if sy > 0 else cy - ARM / 2 - win
                cuts.append(box(x0, y0, deck_z - 1, win, win, DECK + 2))

# wire notches: middle of each wall/rib segment (one per bay side)
for k in (SIZE / 4, 3 * SIZE / 4):
    for y0 in (-1, SIZE / 2 - RIB / 2 - 1, SIZE - WALL - 1):            # walls/rib along x
        cuts.append(box(k - NOTCH_W / 2, y0, deck_z - NOTCH_H, NOTCH_W, max(WALL, RIB) + 2, NOTCH_H))
    for x0 in (-1, SIZE / 2 - RIB / 2 - 1, SIZE - WALL - 1):            # walls/rib along y
        cuts.append(box(x0, k - NOTCH_W / 2, deck_z - NOTCH_H, max(WALL, RIB) + 2, NOTCH_W, NOTCH_H))

# M3 bolt holes through the perimeter walls, 2 per side, at the square boundaries
L = WALL + PAD_T + 2
for k in BOLT_AT:
    for y0 in (-1, SIZE - WALL - PAD_T - 1):
        cuts.append(Part.makeCylinder(BOLT_D / 2, L, V(k, y0, BOLT_Z), V(0, 1, 0)))
    for x0 in (-1, SIZE - WALL - PAD_T - 1):
        cuts.append(Part.makeCylinder(BOLT_D / 2, L, V(x0, k, BOLT_Z), V(1, 0, 0)))

tile = tile.cut(Part.makeCompound(cuts)).removeSplitter()
assert tile.isValid()

os.makedirs(OUT, exist_ok=True)
tile.exportStep(os.path.join(OUT, "sensor_tile.step"))
Mesh.Mesh(MeshPart.meshFromShape(Shape=tile, LinearDeflection=0.02, AngularDeflection=0.2)).write(
    os.path.join(OUT, "sensor_tile.stl"))
# fit-test coupon: one corner square (pocket, slot, walls), ~8 cm3, to check the sensor fit
coupon = tile.common(Part.makeBox(42, 42, HEIGHT)).removeSplitter()
coupon.exportStep(os.path.join(OUT, "sensor_tile_coupon.step"))
Mesh.Mesh(MeshPart.meshFromShape(Shape=coupon, LinearDeflection=0.02, AngularDeflection=0.2)).write(
    os.path.join(OUT, "sensor_tile_coupon.stl"))
bb = tile.BoundBox
print("sensor_tile: %.0f x %.0f x %.0f mm, volume %.0f cm3" % (bb.XLength, bb.YLength, bb.ZLength, tile.Volume / 1000))
