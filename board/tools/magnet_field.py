# Model: where an SS443R switches under different magnet layouts (6 x 3 mm N35 discs).
# Uniformly magnetised cylinders as charged end faces. Prints field over the centre, the
# area above the trip point, and the safe radius (furthest off-centre that still switches
# in every direction). Run: python3 board/tools/magnet_field.py
import numpy as np
Br=1.2; R=3.0
nr,nt=14,36
r=(np.arange(nr)+0.5)/nr*R; t=np.arange(nt)/nt*2*np.pi
rr,tt=np.meshgrid(r,t)
px=(rr*np.cos(tt)).ravel(); py=(rr*np.sin(tt)).ravel(); w=((R/nr)*(2*np.pi/nt)*rr).ravel()
g=np.arange(-20,20.01,0.5); X,Y=np.meshgrid(g,g)
def bz(mags,z):
    # mags: list of (cx,cy,H) ; bottom face at 0, sensor at -z
    B=np.zeros_like(X)
    for cx,cy,H in mags:
        for zf,s in ((0,1),(H,-1)):
            dx=X[...,None]-(cx+px); dy=Y[...,None]-(cy+py); dz=-z-zf
            B+= -s*Br/(4*np.pi)*np.sum(w*dz/(dx*dx+dy*dy+dz*dz)**1.5,axis=-1)
    return B*1000
def grid4(gap,H=6):
    h=(6+gap)/2; return [(a*h,b*h,H) for a in(-1,1) for b in(-1,1)]
ring8=[(x*6,y*6,3) for x in(-1,0,1) for y in(-1,0,1) if (x,y)!=(0,0)]
cfgs=[("1 stack of 2",[(0,0,6)])]+[(f"4 stacks, gap {gp} mm",grid4(gp)) for gp in (0,1,2,3,4,6)]+[("8 singles, ring (3x3 no centre)",ring8)]
for z in (4,5):
  for thr in (13,20.5):
    print(f"\n== magnet face to Hall chip {z} mm, trip {thr} mT ==")
    for name,m in cfgs:
        B=bz(m,z); on=B>=thr
        area=on.sum()*0.25
        # guaranteed radius: largest circle around centre fully 'on'
        rad=np.hypot(X,Y); off=rad[~on]
        rmin=off.min() if on[40,40] else 0.0
        print(f"{name:34s} centre {B[40,40]:6.0f} mT  area {area:6.0f} mm2  safe radius {rmin:4.1f} mm")
