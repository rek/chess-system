# Magnet bases for the chess pieces (FreeCAD script).
# Run from the repo root:  freecadcmd board/case/magnet_base.py
# Writes STEP + STL to board/case/models/ for each layout:
#   magnet_base_<n>   35 mm test puck, pockets open on top (print, drop magnets in)
#   magnet_cutter_<n> just the pocket cylinders, same position: subtract from a piece model
# Layouts (see board/README.md, "Magnet choice per piece"):
#   9: centre + ring of 8 at 10 mm radius     7: centre + 6 (hex flower) at 9 mm radius
import math, os
import FreeCAD as App, Part, Mesh, MeshPart

BASE_DIA   = 35.0   # piece base
FLOOR      = 0.6    # plastic under the magnets (2-3 layers): keep thin, it adds to sensor distance
POCKET_DIA = 6.4    # prints as ~6.1 mm, snug on a 6 mm magnet
POCKET_H   = 3.2    # magnet is 3 mm
LAYOUTS = {9: (8, 10.0), 7: (6, 9.0)}   # magnets: (ring count, ring radius mm), plus a centre one

OUT = os.path.join(os.getcwd(), "board", "case", "models")

def pockets(ring, radius):
    pts = [(0.0, 0.0)] + [(radius * math.cos(2 * math.pi * k / ring),
                           radius * math.sin(2 * math.pi * k / ring)) for k in range(ring)]
    cyls = [Part.makeCylinder(POCKET_DIA / 2, POCKET_H, App.Vector(x, y, FLOOR)) for x, y in pts]
    return cyls[0].fuse(cyls[1:]).removeSplitter()

def save(shape, name):
    shape.exportStep(os.path.join(OUT, name + ".step"))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.1)
    Mesh.Mesh(mesh).write(os.path.join(OUT, name + ".stl"))
    print("wrote", name, "volume %.1f mm3" % shape.Volume)

os.makedirs(OUT, exist_ok=True)
for n, (ring, radius) in LAYOUTS.items():
    cutter = pockets(ring, radius)
    puck = Part.makeCylinder(BASE_DIA / 2, FLOOR + POCKET_H).cut(cutter).removeSplitter()
    save(puck, "magnet_base_%d" % n)
    save(cutter, "magnet_cutter_%d" % n)
