# -*- coding: utf-8 -*-
"""libredwg-web JSON dökümünden seçilen katmanları ezdxf ile bir DXF'e aktarır.

Kullanım (modül):
    conv = JsonToDxf(json_data, doc, dx, dy, prefix='IS_')
    conv.add_entities(filter_fn)

- Bloklar 'prefix + ad' olarak yeniden tanımlanır (anonim *U blokları dahil).
- INSERT öznitelikleri (ATTRIB) WCS'de TEXT olarak yazılır.
- DIMENSION / HATCH / ATTDEF aktarılmaz.
"""
import math
from ezdxf.enums import TextEntityAlignment

HALIGN = {(0, 0): None, (1, 0): TextEntityAlignment.BOTTOM_CENTER, (2, 0): TextEntityAlignment.BOTTOM_RIGHT,
          (0, 1): TextEntityAlignment.BOTTOM_LEFT, (1, 1): TextEntityAlignment.BOTTOM_CENTER, (2, 1): TextEntityAlignment.BOTTOM_RIGHT,
          (0, 2): TextEntityAlignment.MIDDLE_LEFT, (1, 2): TextEntityAlignment.MIDDLE_CENTER, (2, 2): TextEntityAlignment.MIDDLE_RIGHT,
          (0, 3): TextEntityAlignment.TOP_LEFT, (1, 3): TextEntityAlignment.TOP_CENTER, (2, 3): TextEntityAlignment.TOP_RIGHT,
          (4, 0): TextEntityAlignment.MIDDLE, (3, 0): TextEntityAlignment.ALIGNED, (5, 0): TextEntityAlignment.FIT}


def safe(name):
    return ''.join(c if (c.isalnum() or c in '_-') else '_' for c in name)


class JsonToDxf:
    def __init__(self, data, doc, dx=0.0, dy=0.0, prefix='IS_'):
        self.data, self.doc, self.dx, self.dy, self.prefix = data, doc, dx, dy, prefix
        self.msp = doc.modelspace()
        self.blocks = {b.get('name'): b for b in data['tables']['BLOCK_RECORD']['entries']}
        self.defined = {}
        self.layers = {l['name']: l for l in data['tables']['LAYER']['entries']}
        self.styles = {s.get('name'): s for s in data['tables'].get('STYLE', {}).get('entries', [])}
        self.count = 0
        self.attr_map = {}  # INSERT handle -> öznitelik TEXT varlıkları
        self.map = {}   # JSON handle -> (ezdxf varlığı, JSON varlığı)  (yalnız model alanı)

    # ---------------------------------------------------------------- tablolar
    def layer(self, name):
        if name not in self.doc.layers:
            l = self.layers.get(name, {})
            c = l.get('colorIndex', 7)
            self.doc.layers.add(name, color=c if 0 < abs(c) < 256 else 7)
        return name

    def style(self, name):
        if not name:
            return 'Standard'
        if name not in self.doc.styles:
            s = self.styles.get(name, {})
            font = s.get('font') or s.get('fontFile') or 'arial.ttf'
            try:
                self.doc.styles.add(name, font=font if font.lower().endswith(('.ttf', '.shx')) else 'arial.ttf')
            except Exception:
                return 'Standard'
        return name

    # ---------------------------------------------------------------- bloklar
    def block(self, name):
        if name in self.defined:
            return self.defined[name]
        src = self.blocks.get(name)
        bname = self.prefix + safe(name.lstrip('*'))
        self.defined[name] = bname
        if bname in self.doc.blocks:
            self.doc.blocks.delete_block(bname, safe=False)
        bp = (src or {}).get('basePoint', {'x': 0, 'y': 0})
        blk = self.doc.blocks.new(bname, base_point=(bp.get('x', 0), bp.get('y', 0)))
        if src:
            for e in src.get('entities', []):
                self.entity(e, blk, 0.0, 0.0)
        return bname

    # ---------------------------------------------------------------- varlıklar
    def attrs(self, e):
        a = {'layer': self.layer(e.get('layer', '0'))}
        c = e.get('colorIndex', 256)
        if c != 256:
            a['color'] = c
        return a

    def P(self, p, dx, dy):
        return (p['x'] + dx, p['y'] + dy)

    def text(self, t, a, space, dx, dy, value=None):
        """TEXT veya ATTRIB'in text alt sözlüğü."""
        s = value if value is not None else t.get('text', '')
        if not s:
            return
        h = t.get('textHeight', 2.5) or 2.5
        a = dict(a)
        a['style'] = self.style(t.get('styleName'))
        a['rotation'] = math.degrees(t.get('rotation', 0) or 0)
        if t.get('xScale', 1) not in (0, 1):
            a['width'] = t['xScale']
        ent = space.add_text(s, height=h, dxfattribs=a)
        al = HALIGN.get((t.get('halign', 0), t.get('valign', 0)))
        p1 = self.P(t['startPoint'], dx, dy)
        if al is None:
            ent.dxf.insert = p1
        else:
            p2 = self.P(t['endPoint'], dx, dy) if t.get('endPoint') and (t['endPoint']['x'] or t['endPoint']['y']) else p1
            if al in (TextEntityAlignment.ALIGNED, TextEntityAlignment.FIT):
                ent.set_placement(p1, p2, align=al)
            else:
                ent.set_placement(p2, align=al)
        self.count += 1
        return ent

    def entity(self, e, space, dx, dy):
        t = e['type']
        try:
            if t == 'LINE':
                space.add_line(self.P(e['startPoint'], dx, dy), self.P(e['endPoint'], dx, dy), dxfattribs=self.attrs(e))
            elif t == 'LWPOLYLINE':
                pts = [(v['x'] + dx, v['y'] + dy, 0, 0, v.get('bulge', 0) or 0) for v in e.get('vertices', [])]
                if len(pts) < 2:
                    return
                a = self.attrs(e)
                if e.get('constantWidth'):
                    a['const_width'] = e['constantWidth']
                pl = space.add_lwpolyline(pts, format='xyseb', close=bool(e.get('flag', 0) & 1), dxfattribs=a)
                if space is self.msp:
                    self.map[e['handle']] = (pl, e)
            elif t == 'CIRCLE':
                space.add_circle(self.P(e['center'], dx, dy), e['radius'], dxfattribs=self.attrs(e))
            elif t == 'ARC':
                space.add_arc(self.P(e['center'], dx, dy), e['radius'], math.degrees(e['startAngle']), math.degrees(e['endAngle']), dxfattribs=self.attrs(e))
            elif t == 'ELLIPSE':
                c = self.P(e['center'], dx, dy); m = e['majorAxisEndPoint']
                space.add_ellipse(c, (m['x'], m['y'], 0), e.get('axisRatio', 1), e.get('startAngle', 0), e.get('endAngle', math.tau), dxfattribs=self.attrs(e))
            elif t == 'SOLID':
                pts = [self.P(e[k], dx, dy) for k in ('corner1', 'corner2', 'corner3', 'corner4') if isinstance(e.get(k), dict)]
                if len(pts) >= 3:
                    space.add_solid(pts, dxfattribs=self.attrs(e))
            elif t == 'TEXT':
                self.text(e, self.attrs(e), space, dx, dy)
            elif t == 'MTEXT':
                s = e.get('text', '')
                if not s:
                    return
                a = self.attrs(e)
                a['char_height'] = e.get('textHeight', 2.5) or 2.5
                a['style'] = self.style(e.get('styleName'))
                a['attachment_point'] = e.get('attachmentPoint', 1) or 1
                if e.get('rectWidth') or e.get('width'):
                    a['width'] = e.get('rectWidth') or e.get('width')
                d = e.get('direction') or e.get('xAxisDirection')
                if isinstance(d, dict) and (d.get('x') or d.get('y')):
                    a['rotation'] = math.degrees(math.atan2(d.get('y', 0), d.get('x', 1)))
                m = space.add_mtext(s, dxfattribs=a)
                m.dxf.insert = self.P(e['insertionPoint'], dx, dy)
                self.count += 1
            elif t == 'INSERT':
                bname = self.block(e['name'])
                a = self.attrs(e)
                a.update(xscale=e.get('xScale', 1) or 1, yscale=e.get('yScale', 1) or 1, zscale=e.get('zScale', 1) or 1,
                         rotation=math.degrees(e.get('rotation', 0) or 0))
                ref = space.add_blockref(bname, self.P(e['insertionPoint'], dx, dy), dxfattribs=a)
                if space is self.msp:
                    self.map[e['handle']] = (ref, e)
                    ref.set_xdata('JSONH', [(1000, e['handle'])]) if 'JSONH' in self.doc.appids else None
                for at in e.get('attribs', []) or []:
                    tt = at.get('text')
                    if isinstance(tt, dict) and at.get('isVisible', True) and not (at.get('flags', 0) & 1):
                        te = self.text(tt, self.attrs(at), space, dx, dy)
                        if te is not None and space is self.msp:
                            self.attr_map.setdefault(e['handle'], []).append(te)
            else:
                return
            self.count += 1
        except Exception:
            pass

    def add_entities(self, keep):
        for e in self.data['entities']:
            if e['type'] in ('ATTRIB', 'ATTDEF'):
                continue
            if keep(e):
                self.entity(e, self.msp, self.dx, self.dy)
        return self.count
