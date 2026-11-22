# Model: compare magnet layouts (6 x 3 mm N35 discs, up to 9 per piece) under an SS443R,
# Hall chip 5 mm below the magnets. Uniformly magnetised cylinders as charged end faces.
# Prints, best first: field over the centre, safe radius (furthest off-centre that still
# switches in every direction) for worst-case 20.5 mT / typical 13 mT trip points, and
# reach (furthest point a most-sensitive 4.5 mT sensor would switch, for crosstalk).
# Run: python3 board/tools/magnet_field.py (takes ~1.5 min)
import numpy as np, math
Br=1.2; R=3.0
nr,nt=8,24
r=(np.arange(nr)+0.5)/nr*R; t=np.arange(nt)/nt*2*np.pi
rr,tt=np.meshgrid(r,t)
px=(rr*np.cos(tt)).ravel(); py=(rr*np.sin(tt)).ravel(); w=((R/nr)*(2*np.pi/nt)*rr).ravel()
g=np.arange(-32,32.01,0.5); X,Y=np.meshgrid(g,g); C=len(g)//2; RAD=np.hypot(X,Y)
def bz(mags,z):
    B=np.zeros_like(X)
    for cx,cy,H in mags:
        for zf,s in ((0,1),(H,-1)):
            dx=X[...,None]-(cx+px); dy=Y[...,None]-(cy+py); dz=-z-zf
            B+= -s*Br/(4*np.pi)*np.sum(w*dz/(dx*dx+dy*dy+dz*dz)**1.5,axis=-1)
    return B*1000
def safe(B,thr):
    on=B>=thr; return 0.0 if not on[C,C] else RAD[~on].min()
def reach(B,thr):
    on=B>=thr; return RAD[on].max() if on.any() else 0
def polyg(n,rad,H,off=0): return [(rad*math.cos(2*math.pi*k/n+off),rad*math.sin(2*math.pi*k/n+off),H) for k in range(n)]
def grid(n,p,H):
    o=(n-1)/2; return [((i-o)*p,(j-o)*p,H) for i in range(n) for j in range(n)]
cf=[]
for p in (7,8,9,10,11):
    cf.append((f"hex7 singles pitch {p}",7,[(0,0,3)]+polyg(6,p,3)))
    cf.append((f"3x3 singles pitch {p}",9,grid(3,p,3)))
    cf.append((f"2x2 stacks2 pitch {p}",8,grid(2,p,6)))
    cf.append((f"ring8 singles r {p}",8,polyg(8,p,3)))
    cf.append((f"centre+ring8 r {p}",9,[(0,0,3)]+polyg(8,p,3)))
    cf.append((f"tri stacks3 r {p}",9,polyg(3,p,9,math.pi/2)))
    cf.append((f"2x2 stacks2 + centre1 pitch {p}",9,grid(2,p*1.414,6)+[(0,0,3)]))
for p in (12,13,14):
    cf.append((f"centre+ring8 r {p}",9,[(0,0,3)]+polyg(8,p,3)))
    cf.append((f"ring8 singles r {p}",8,polyg(8,p,3)))
    cf.append((f"hex7 singles pitch {p}",7,[(0,0,3)]+polyg(6,p,3)))
z=5.0
rows=[]
for name,n,m in cf:
    span=2*(max(math.hypot(x,y) for x,y,_ in m)+3.1)
    if span>33.5: continue
    B=bz(m,z)
    rows.append((safe(B,20.5),name,n,B[C,C],safe(B,13),reach(B,4.5),span))
rows.sort(reverse=True)
print("chip 5 mm below magnets. safe radius worst/typ, max reach for most-sensitive sensor (4.5 mT)")
for s,name,n,c,st,re,span in rows[:22]:
    print(f"{name:32s} {n} mags span {span:4.1f}  centre {c:4.0f}  safe {s:4.1f}/{st:4.1f}  reach {re:4.1f}")
