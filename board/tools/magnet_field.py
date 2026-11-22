# Model: field at the sensor below 4 magnet stacks (6 mm dia x 6 mm tall, N35) vs spacing.
# Uniformly magnetised cylinders as charged end faces. Run: python3 board/tools/magnet_field.py
import numpy as np
Br=1.2; R=3.0; H=6.0
nr,nt=40,72
r=(np.arange(nr)+0.5)/nr*R; t=np.arange(nt)/nt*2*np.pi
rr,tt=np.meshgrid(r,t); dA=(R/nr)*(2*np.pi/nt)*rr
px=(rr*np.cos(tt)).ravel(); py=(rr*np.sin(tt)).ravel(); w=dA.ravel()
def bz_disc(cx,cy,zf,x,y,z,s):
    dx=x-(cx+px); dy=y-(cy+py); dz=z-zf
    d3=(dx*dx+dy*dy+dz*dz)**1.5
    return s*Br/(4*np.pi)*np.sum(w*dz/d3)
def bz(centres,x,y,z):
    # bottom face at z=0 (pole facing sensor, +), top face at z=H (-); sensor at z<0
    b=0
    for cx,cy in centres:
        b+=bz_disc(cx,cy,0,x,y,z,1)+bz_disc(cx,cy,H,x,y,z,-1)
    return -b  # field magnitude toward sensor
def cluster(gap):
    h=(6+gap)/2
    return [(h,h),(-h,h),(h,-h),(-h,-h)]
single=[(0,0)]
for d in (3,5,8):
    ref=bz(single,0,0,-d)
    print(f"\n--- sensor {d} mm below magnet face; single stack centre = {ref*1000:.0f} mT")
    print("gap(mm)  centre  6mm-off  10mm-off  14mm-off   (mT)")
    for gap in (0,1,2,3,4,6,9):
        c=cluster(gap)
        vals=[bz(c,x,0,-d)*1000 for x in (0,6,10,14)]
        print(f"{gap:5}   "+"  ".join(f"{v:7.0f}" for v in vals))
