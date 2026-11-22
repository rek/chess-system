# Sensor holder tile for the board underside (FreeCAD script).
# Run from the repo root:  freecadcmd board/case/sensor_tile.py
# Writes board/case/models/sensor_tile.step (+ .stl). Print 4, all identical.
#
# One tile = 4 x 4 squares (160 x 160 mm) = 16 SS443R sensors = one MCP23017.
# Print it upside down (deck on the bed): the deck top comes out flat for the 3 mm sheet,
# and nothing needs supports.
#
#   deck (3 mm) with a pocket at every square centre: sensor face up, flush with the top
#   lead slot beside each pocket: bend the 3 leads straight down through it
#   perimeter walls + one cross rib, 20 mm deep: 4 open bays underneath for wiring,
#     the MCP23017 module and (on one tile) the Pico
#   wall holes: M3 bolts join neighbouring tiles (same holes on all 4 sides, so the tile
#     works in any corner, rotated)
#   notches at the bottom of walls and ribs: wires pass between bays and tiles
import os
import FreeCAD as App, Part, Mesh, MeshPart
V = App.Vector

SQUARE   = 40.0           # chess square
N        = 4              # squares per side per tile
SIZE     = SQUARE * N     # 160 mm
HEIGHT   = 20.0           # total tile height (deck + bays)
DECK     = 3.0            # deck thickness
WALL     = 2.0            # perimeter wall (two tiles side by side = 4 mm)
RIB      = 2.0            # cross rib at the tile centre lines

SENSOR_W, SENSOR_H, SENSOR_T = 4.1, 3.1, 1.6   # measured body: width, height (lead axis), thickness
CLEAR    = 0.15           # per side, snug fit
SLOT_W, SLOT_D = SENSOR_W + 2 * CLEAR, 1.5     # lead slot, beside the lead edge of the pocket

BOLT_D   = 3.4            # M3 clearance
BOLT_Z   = 10.0           # bolt height above the bottom edge
NOTCH_W, NOTCH_H = 12.0, 8.0   # wire notch at the bottom of walls/ribs

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

# wire notches: middle of each wall/rib segment (one per bay side)
for k in (SIZE / 4, 3 * SIZE / 4):
    for y0 in (-1, SIZE / 2 - RIB / 2 - 1, SIZE - WALL - 1):            # walls/rib along x
        cuts.append(box(k - NOTCH_W / 2, y0, -1, NOTCH_W, WALL + 2, NOTCH_H + 1))
    for x0 in (-1, SIZE / 2 - RIB / 2 - 1, SIZE - WALL - 1):            # walls/rib along y
        cuts.append(box(x0, k - NOTCH_W / 2, -1, WALL + 2, NOTCH_W, NOTCH_H + 1))

# M3 bolt holes through the perimeter walls, 2 per side, at the square boundaries
for k in (SQUARE, SIZE - SQUARE):
    for y0 in (-1, SIZE - WALL - 1):
        cuts.append(Part.makeCylinder(BOLT_D / 2, WALL + 2, V(k, y0, BOLT_Z), V(0, 1, 0)))
    for x0 in (-1, SIZE - WALL - 1):
        cuts.append(Part.makeCylinder(BOLT_D / 2, WALL + 2, V(x0, k, BOLT_Z), V(1, 0, 0)))

tile = tile.cut(Part.makeCompound(cuts)).removeSplitter()
assert tile.isValid()

os.makedirs(OUT, exist_ok=True)
tile.exportStep(os.path.join(OUT, "sensor_tile.step"))
Mesh.Mesh(MeshPart.meshFromShape(Shape=tile, LinearDeflection=0.02, AngularDeflection=0.2)).write(
    os.path.join(OUT, "sensor_tile.stl"))
bb = tile.BoundBox
print("sensor_tile: %.0f x %.0f x %.0f mm, volume %.0f cm3" % (bb.XLength, bb.YLength, bb.ZLength, tile.Volume / 1000))
