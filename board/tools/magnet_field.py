# Model: compare magnet layouts (6 x 3 mm N35 discs) under an SS443R, Hall chip 4.5 mm below.
# Prints, per magnet count, the best layouts: field over the centre, safe radius (furthest
# off-centre that still switches in every direction) for worst-case 20.5 mT and typical
# 13 mT trip points, and footprint. Run: python3 board/tools/magnet_field.py (takes ~3 min)
import numpy as np
Br=1.2; R=3.0
nr,nt=10,30
r=(np.arange(nr)+0.5)/nr*R; t=np.arange(nt)/nt*2*np.pi
rr,tt=np.meshgrid(r,t)
px=(rr*np.cos(tt)).ravel(); py=(rr*np.sin(tt)).ravel(); w=((R/nr)*(2*np.pi/nt)*rr).ravel()
g=np.arange(-22,22.01,0.5); X,Y=np.meshgrid(g,g); C=len(g)//2
RAD=np.hypot(X,Y)
def bz(mags,z):
    B=np.zeros_like(X)
    for cx,cy,H in mags:
        for zf,s in ((0,1),(H,-1)):
            dx=X[...,None]-(cx+px); dy=Y[...,None]-(cy+py); dz=-z-zf
            B+= -s*Br/(4*np.pi)*np.sum(w*dz/(dx*dx+dy*dy+dz*dz)**1.5,axis=-1)
    return B*1000
def safe(B,thr):
    on=B>=thr
    return 0.0 if not on[C,C] else RAD[~on].min()
L=[]
def grid(n,pitch,H): # n x n grid
    o=(n-1)/2; return [((i-o)*pitch,(j-o)*pitch,H) for i in range(n) for j in range(n)]
def ring(pitch,H): return [(x*pitch,y*pitch,H) for x in(-1,0,1) for y in(-1,0,1) if (x,y)!=(0,0)]
def dice5(pitch,H): return [(0,0,H)]+[(a*pitch,b*pitch,H) for a in(-1,1) for b in(-1,1)]
def hexring(rad,H,centre):
    m=[(rad*np.cos(k*np.pi/3),rad*np.sin(k*np.pi/3),H) for k in range(6)]
    return m+([(0,0,H)] if centre else [])
for gap in (0,1.5,3,4.5,6):
    p=6+gap
    L+= [(f"2x2 singles gap {gap}",4,grid(2,p,3)),(f"2x2 stacks2 gap {gap}",8,grid(2,p,6)),
         (f"ring8 singles gap {gap}",8,ring(p,3)),(f"3x3 singles gap {gap}",9,grid(3,p,3)),
         (f"dice5 singles gap {gap}",5,dice5(p,3)),(f"hex6 singles gap {gap}",6,hexring(p,3,False)),
         (f"hex7 singles gap {gap}",7,hexring(p,3,True))]
L+=[("1 single",1,[(0,0,3)]),("1 stack2",2,[(0,0,6)])]
res=[]
for name,n,m in L:
    B=bz(m,4.5)
    ext=max(np.hypot(x,y) for x,y,_ in m)+3
    res.append((name,n,B[C,C],safe(B,20.5),safe(B,13),2*ext, B[C, np.searchsorted(g,22)-1] if True else 0))
for n in sorted(set(r[1] for r in res)):
    best=sorted([r for r in res if r[1]==n and r[2]>=30],key=lambda r:-r[3])[:3]
    for r in best: print(f"{r[1]} mags  {r[0]:24s} centre {r[2]:5.0f}  safeR worst {r[3]:4.1f} typ {r[4]:4.1f}  footprint {r[5]:4.1f} mm  field@22mm {r[6]:.1f}")
