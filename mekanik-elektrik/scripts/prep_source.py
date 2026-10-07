# -*- coding: utf-8 -*-
"""Kullanıcının revize ettiği DXF'ten (guc2) MEK-ELK katmanlarını ve 07 pafta çerçeve kopyasını temizler;
mimari ve kullanıcı çizimleri korunur. Sonuç build_dxf.py'ye kaynak olarak verilir."""
import sys, ezdxf
src, out = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(src); msp = doc.modelspace()
rm = [e for e in msp if e.dxf.layer.startswith('MEK-ELK')]
fr = [e for e in msp.query('INSERT') if abs(e.dxf.insert.x - 26612.547) < 2 and abs(e.dxf.insert.y - 13.05) < 6]
print('silinen MEK:', len(rm), 'çerçeve:', len(fr), [e.dxf.name for e in fr])
for e in rm + fr:
    msp.delete_entity(e)
f = [e for e in msp.query('INSERT') if abs(e.dxf.insert.x - 2309.806) < 2 and e.attribs]
print('zemin çerçeve blok adı:', [(e.dxf.name, round(e.dxf.insert.y, 1)) for e in f])
doc.saveas(out)
