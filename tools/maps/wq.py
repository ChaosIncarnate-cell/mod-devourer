"""Map and DBC readers for the quest tools (the server's own extracted data on the owner's PC; nothing of it is
committed). q() reads the world database with QUEST_DB_USER / QUEST_DB_PASS from the environment."""
import os, struct, subprocess, functools
MYSQL=r'Z:\ChromaticawBots\mysql\bin\mysql.exe'
DBC='Z:/ChromaticawBots/server/data/dbc/'
def q(sql, db='acore_world'):
    r=subprocess.run([MYSQL,'-u'+os.environ.get('QUEST_DB_USER',''),'-p'+os.environ.get('QUEST_DB_PASS',''),db,'-B','-N','-e',sql],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode: raise RuntimeError(r.stderr)
    return [l.split('\t') for l in r.stdout.splitlines() if l]
def dbc(name):
    d=open(DBC+name,'rb').read(); n,fc,rs,ss=struct.unpack_from('<4I',d,4)
    strs=d[20+n*rs:]
    def s(o): return strs[o:strs.index(b'\0',o)].decode('utf-8','replace')
    rows=[d[20+i*rs:20+(i+1)*rs] for i in range(n)]
    return rows,s
@functools.lru_cache()
def zones():
    rows,s=dbc('WorldMapArea.dbc'); out=[]
    arows,as_=dbc('AreaTable.dbc'); aname={}
    for r in arows:
        i=struct.unpack_from('<I',r,0)[0]; aname[i]=as_(struct.unpack_from('<I',r,11*4)[0])
    for r in rows:
        i,mp,area=struct.unpack_from('<3I',r,0); l,rr,t,b=struct.unpack_from('<4f',r,16)
        if area==0: continue
        out.append((mp,area,aname.get(area,s(struct.unpack_from('<I',r,12)[0])),l,rr,t,b))
    return out
def zone_of(mp,x,y):
    best=None
    for z in zones():
        m,a,n,l,r,t,b=z
        if m==mp and r<=y<=l and b<=x<=t:
            area=(l-r)*(t-b)
            if not best or area<best[0]: best=(area,n)
    return best[1] if best else '?map%d'%mp

MAPS='Z:/ChromaticawBots/server/data/maps/'
@functools.lru_cache()
def areas():
    rows,s=dbc('AreaTable.dbc'); out={}
    for r in rows:
        i,mp,parent=struct.unpack_from('<3I',r,0)
        out[i]=(parent,s(struct.unpack_from('<I',r,11*4)[0]))
    return out
@functools.lru_cache(maxsize=4096)
def _tile(mp,gx,gy):
    try: d=open(MAPS+'%03d%02d%02d.map'%(mp,gx,gy),'rb').read()
    except OSError: return None
    off=struct.unpack_from('<I',d,12)[0]
    fourcc,flags,grid=struct.unpack_from('<IHH',d,off)
    if flags&1: return grid
    return struct.unpack_from('<256H',d,off+8)
def area_of(mp,x,y):
    G=533.3333333
    gx=int(32-x/G); gy=int(32-y/G)
    t=_tile(mp,gx,gy)
    if t is None: return 0
    if isinstance(t,int): return t
    lx=int(16*(32-x/G))&15; ly=int(16*(32-y/G))&15
    return t[lx*16+ly]
def zone_area(mp,x,y):
    a=area_of(mp,x,y); A=areas()
    if not a or a not in A: return ('?','?')
    parent,name=A[a]
    zone=A[parent][1] if parent and parent in A else name
    return (zone,name)

@functools.lru_cache(maxsize=512)
def _htile(mp,gx,gy):
    try: d=open(MAPS+'%03d%02d%02d.map'%(mp,gx,gy),'rb').read()
    except OSError: return None
    off=struct.unpack_from('<I',d,20)[0]
    fourcc,flags,gh,gmax=struct.unpack_from('<IIff',d,off)
    p=off+16
    if flags&1: return ('flat',gh)
    if flags&2:
        v9=struct.unpack_from('<16641H',d,p); v8=struct.unpack_from('<16384H',d,p+16641*2); m=(gmax-gh)/65535
    elif flags&4:
        v9=struct.unpack_from('<16641B',d,p); v8=struct.unpack_from('<16384B',d,p+16641); m=(gmax-gh)/255
    else:
        v9=struct.unpack_from('<16641f',d,p); v8=struct.unpack_from('<16384f',d,p+16641*4); m=None
    if m is not None:
        v9=[v*m+gh for v in v9]; v8=[v*m+gh for v in v8]
    return ('grid',v9,v8)
def height(mp,x,y):
    G=533.3333333
    gx=int(32-x/G); gy=int(32-y/G)
    t=_htile(mp,gx,gy)
    if t is None: return None
    if t[0]=='flat': return t[1]
    v9,v8=t[1],t[2]
    fx=128*(32-x/G); fy=128*(32-y/G)
    xi=int(fx); yi=int(fy); fx-=xi; fy-=yi; xi&=127; yi&=127
    h5=2*v8[xi*128+yi]
    if fx+fy<1:
        if fx>fy:
            h1=v9[xi*129+yi]; h2=v9[(xi+1)*129+yi]; a=h2-h1; b=h5-h1-h2; c=h1
        else:
            h1=v9[xi*129+yi]; h3=v9[xi*129+yi+1]; a=h5-h1-h3; b=h3-h1; c=h1
    else:
        if fx>fy:
            h2=v9[(xi+1)*129+yi]; h4=v9[(xi+1)*129+yi+1]; a=h2+h4-h5; b=h4-h2; c=h5-h4
        else:
            h3=v9[xi*129+yi+1]; h4=v9[(xi+1)*129+yi+1]; a=h4-h3; b=h3+h4-h5; c=h5-h4
    return a*fx+b*fy+c

@functools.lru_cache(maxsize=512)
def _ltile(mp,gx,gy):
    try: d=open(MAPS+'%03d%02d%02d.map'%(mp,gx,gy),'rb').read()
    except OSError: return None
    off=struct.unpack_from('<I',d,28)[0]
    if not off: return None
    fourcc,flags,lflags,ltype,ox,oy,w,h,level=struct.unpack_from('<IBBHBBBBf',d,off)
    p=off+16; fl=None; lmap=None
    if not flags&1:
        p+=512; fl=struct.unpack_from('<256B',d,p); p+=256
    if not flags&2:
        lmap=struct.unpack_from('<%df'%(w*h),d,p)
    return (lflags,fl,ox,oy,w,h,level,lmap)
def water(mp,x,y):
    """liquid level above the ground here, or None"""
    G=533.3333333
    gx=int(32-x/G); gy=int(32-y/G)
    t=_ltile(mp,gx,gy)
    if not t: return None
    lflags,fl,ox,oy,w,h,level,lmap=t
    lx=int(16*(32-x/G))&15; ly=int(16*(32-y/G))&15
    f=fl[lx*16+ly] if fl else lflags
    if not f: return None
    if lmap is None: lv=level
    else:
        cx=(int(128*(32-x/G))&127)-oy; cy=(int(128*(32-y/G))&127)-ox
        if cx<0 or cx>=h or cy<0 or cy>=w: return None
        lv=lmap[cx*w+cy]
    hz=height(mp,x,y)
    return lv if hz is None or lv>hz+0.2 else None

def ground(mp,x,y):
    """(z, slope, water, zone, area) of a spot"""
    z=height(mp,x,y)
    if z is None: return None
    hs=[height(mp,x+dx,y+dy) for dx,dy in ((2,0),(-2,0),(0,2),(0,-2))]
    slope=max(abs(h-z) for h in hs if h is not None)
    zone,area=zone_area(mp,x,y)
    return (round(z,2),round(slope,2),water(mp,x,y),zone,area)
