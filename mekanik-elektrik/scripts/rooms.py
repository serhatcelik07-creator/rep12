import ezdxf, json, ezdxf.path
doc=ezdxf.readfile('temiz1.dxf'); msp=doc.modelspace()
segs=[]
def addseg(e):
    t=e.dxftype()
    if t=='LINE': segs.append((e.dxf.start.x,e.dxf.start.y,e.dxf.end.x,e.dxf.end.y))
    elif t in('LWPOLYLINE','POLYLINE','ARC'):
        pts=[(p.x,p.y) for p in ezdxf.path.make_path(e).flattening(2)]
        for a,b in zip(pts,pts[1:]): segs.append((a[0],a[1],b[0],b[1]))
WL=('WALL','GLAZ','VITRF','STRC','CERCEVE','SHAFT','ALUMINIUM','MYM_CAM','DOOR-FRAM')
for e in msp:
    L=e.dxf.layer
    if e.dxftype()=='INSERT':
        if any(k in L for k in ('GLAZ','ALUMINIUM','WINDOW','DOOR')):
            try:
                for v in e.virtual_entities(): addseg(v)
            except Exception: pass
        continue
    if any(k in L for k in WL): addseg(e)
print(len(segs))
def ray(x,y,dx,dy,maxd=1500):
    best=maxd
    for x1,y1,x2,y2 in segs:
        if dx:  # horizontal ray
            if (y1-y)*(y2-y)>0 or y1==y2: continue
            xi=x1+(y-y1)*(x2-x1)/(y2-y1); d=(xi-x)*dx
        else:
            if (x1-x)*(x2-x)>0 or x1==x2: continue
            yi=y1+(x-x1)*(y2-y1)/(x2-x1); d=(yi-y)*dy
        if 3<d<best: best=d
    return best
rooms=[]
for e in msp.query('INSERT'):
    a={x.dxf.tag:x.dxf.text for x in e.attribs}
    if 'MAHALADI' in a:
        x,y=e.dxf.insert.x,e.dxf.insert.y
        # tag text sits at insert; probe slightly below tag center
        px,py=x+40,y-20
        l=ray(px,py,-1,0);r=ray(px,py,1,0);d=ray(px,py,0,-1);u=ray(px,py,0,1)
        bb=[px-l,py-d,px+r,py+u]
        # second pass from bbox center for robustness
        cx,cy=(bb[0]+bb[2])/2,(bb[1]+bb[3])/2
        l=ray(cx,cy,-1,0);r=ray(cx,cy,1,0);d=ray(cx,cy,0,-1);u=ray(cx,cy,0,1)
        bb2=[cx-l,cy-d,cx+r,cy+u]
        rooms.append(dict(name=a['MAHALADI'],no=a.get('00'),kat=a.get('K'),area=a.get('27.00'),tag=(x,y),bb=[round(v) for v in bb2]))
        w=(bb2[2]-bb2[0])/100;h=(bb2[3]-bb2[1])/100
        print(a.get('K'),a.get('00'),a['MAHALADI'],a.get('27.00'),[round(v) for v in bb2], f"{w:.2f}x{h:.2f}={w*h:.1f}")
json.dump(rooms,open('rooms.json','w'),ensure_ascii=False,indent=0)
