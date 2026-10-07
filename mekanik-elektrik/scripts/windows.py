import ezdxf, json
from ezdxf import bbox
doc=ezdxf.readfile('temiz1.dxf'); msp=doc.modelspace()
SIZE={'-KM-AL1 150_900':(1.40,3.50,'AL1'),'-KM-AL5 140_164':(1.40,3.50,'AL5'),'*U77':(1.60,3.20,'P3'),'*U147':(1.60,3.20,'P3'),'*U176':(1.60,3.20,'P3'),
      '*U184':(0.85,1.00,'P5'),'*U206':(1.30,3.00,'P5'),'*U276':(1.00,2.50,'P3'),'*U278':(1.30,3.00,'P5'),'*U295':(1.30,3.00,'P5')}
out=[]
for e in msp.query('INSERT'):
    n=e.dxf.name
    if n in SIZE and e.dxf.layer=='Z_MİM_-KM-GLAZ':
        b=bbox.extents([e]); c=b.center
        w,h,t=SIZE[n]
        out.append(dict(x=c.x,y=c.y,rot=round(e.dxf.rotation),w=w,h=h,tip=t))
json.dump(out,open('windows.json','w'))
print(len(out))
