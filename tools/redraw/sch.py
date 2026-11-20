"""Small vector schematic toolkit on top of a reportlab canvas.
All coordinates are local, y pointing DOWN; converted at draw time."""
import math
from reportlab.lib import colors

INK = colors.HexColor("#111111")
FONT = "LSans"
FONTB = "LSansB"


class S:
    def __init__(self, c, ox, oy, scale=1.0, lw=1.1):
        self.c, self.ox, self.oy, self.s = c, ox, oy, scale
        self.lw = lw
        c.setStrokeColor(INK)
        c.setFillColor(INK)
        c.setLineWidth(lw * scale)
        c.setLineCap(1)
        c.setLineJoin(1)

    # ---- coordinate conversion
    def X(self, x):
        return self.ox + x * self.s

    def Y(self, y):
        return self.oy - y * self.s

    def _lw(self, w=None):
        self.c.setLineWidth((w or self.lw) * self.s)

    # ---- basic primitives
    def line(self, *pts, w=None, dash=None):
        self._lw(w)
        if dash:
            self.c.setDash([d * self.s for d in dash])
        p = self.c.beginPath()
        p.moveTo(self.X(pts[0][0]), self.Y(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(self.X(x), self.Y(y))
        self.c.drawPath(p, stroke=1, fill=0)
        if dash:
            self.c.setDash([])

    def wire(self, *pts, hops=()):
        """Polyline; hops = list of (x,y) points on the polyline where a
        semicircular crossover bump is drawn."""
        if not hops:
            return self.line(*pts)
        r = 4.5
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            hs = [h for h in hops if self._on_seg(h, (x1, y1), (x2, y2))]
            if not hs:
                self.line((x1, y1), (x2, y2))
                continue
            horiz = y1 == y2
            if horiz:
                sgn = 1 if x2 > x1 else -1
                hs.sort(key=lambda h: sgn * h[0])
                cur = x1
                for hx, _ in hs:
                    self.line((cur, y1), (hx - sgn * r, y1))
                    self._arc_h(hx, y1, r)
                    cur = hx + sgn * r
                self.line((cur, y1), (x2, y2))
            else:
                sgn = 1 if y2 > y1 else -1
                hs.sort(key=lambda h: sgn * h[1])
                cur = y1
                for _, hy in hs:
                    self.line((x1, cur), (x1, hy - sgn * r))
                    self._arc_v(x1, hy, r)
                    cur = hy + sgn * r
                self.line((x1, cur), (x2, y2))

    @staticmethod
    def _on_seg(h, a, b):
        (hx, hy), (x1, y1), (x2, y2) = h, a, b
        if y1 == y2 == hy:
            return min(x1, x2) < hx < max(x1, x2)
        if x1 == x2 == hx:
            return min(y1, y2) < hy < max(y1, y2)
        return False

    def _arc_h(self, x, y, r):  # bump upward
        self._lw()
        p = self.c.beginPath()
        p.arc(self.X(x - r), self.Y(y + r), self.X(x + r), self.Y(y - r), 0, 180)
        self.c.drawPath(p, stroke=1, fill=0)

    def _arc_v(self, x, y, r):  # bump to the right
        self._lw()
        p = self.c.beginPath()
        p.arc(self.X(x - r), self.Y(y + r), self.X(x + r), self.Y(y - r), -90, 180)
        self.c.drawPath(p, stroke=1, fill=0)

    def dot(self, x, y, r=2.4):
        self.c.circle(self.X(x), self.Y(y), r * self.s, stroke=0, fill=1)

    def ocircle(self, x, y, r=2.6, w=None):
        self._lw(w or 0.9)
        self.c.setFillColor(colors.white)
        self.c.circle(self.X(x), self.Y(y), r * self.s, stroke=1, fill=1)
        self.c.setFillColor(INK)

    def term(self, x, y, lab=None):
        self.dot(x, y, 3.2)

    def text(self, x, y, s, size=8, anchor="l", font=None, ital=False):
        f = font or FONT
        self.c.setFont(f, size * self.s)
        X, Y = self.X(x), self.Y(y)
        for i, ln in enumerate(s.split("\n")):
            yy = Y - i * size * 1.15 * self.s
            if anchor == "l":
                self.c.drawString(X, yy, ln)
            elif anchor == "c":
                self.c.drawCentredString(X, yy, ln)
            else:
                self.c.drawRightString(X, yy, ln)

    def arrowhead(self, x, y, ang, size=6):
        """filled head with tip at (x,y), pointing along angle (deg, y-down)."""
        a = math.radians(ang)
        bx, by = x - size * math.cos(a), y - size * math.sin(a)
        px, py = -math.sin(a) * size * 0.38, math.cos(a) * size * 0.38
        p = self.c.beginPath()
        p.moveTo(self.X(x), self.Y(y))
        p.lineTo(self.X(bx + px), self.Y(by + py))
        p.lineTo(self.X(bx - px), self.Y(by - py))
        p.close()
        self.c.drawPath(p, stroke=0, fill=1)

    def arrow(self, *pts, size=6, w=None):
        self.line(*pts, w=w)
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        self.arrowhead(x2, y2, math.degrees(math.atan2(y2 - y1, x2 - x1)), size)

    def rect(self, x1, y1, x2, y2, w=None, dash=None):
        self.line((x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1), w=w, dash=dash)

    # ---- components (axis aligned two-terminal parts)
    def _axis(self, p1, p2, body):
        (x1, y1), (x2, y2) = p1, p2
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        a = (mx - ux * body / 2, my - uy * body / 2)
        b = (mx + ux * body / 2, my + uy * body / 2)
        return a, b, (ux, uy), (mx, my)

    def res(self, p1, p2, body=30, amp=4.2, n=6):
        a, b, (ux, uy), _ = self._axis(p1, p2, body)
        self.line(p1, a)
        self.line(b, p2)
        nx, ny = -uy, ux
        pts = [a]
        for i in range(n):
            t = (i + 0.5) / n
            sg = 1 if i % 2 == 0 else -1
            pts.append((a[0] + ux * body * t + nx * amp * sg,
                        a[1] + uy * body * t + ny * amp * sg))
        pts.append(b)
        self.line(*pts)
        return a, b

    def pot(self, p1, p2, side=-1, body=34, wiper_len=16):
        """variable resistor; wiper arrow enters from `side`
        (vertical part: -1 left/+1 right; horizontal part: -1 above/+1 below).
        returns the wiper tail point."""
        self.res(p1, p2, body=body)
        (x1, y1), (x2, y2) = p1, p2
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if x1 == x2:
            tail, tip = (mx + side * wiper_len, my), (mx + side * 5, my)
        else:
            tail, tip = (mx, my + side * wiper_len), (mx, my + side * 5)
        self.arrow(tail, tip, size=6)
        return tail

    def trimpot(self, p1, p2, body=30):
        self.res(p1, p2, body=body)
        _, _, (ux, uy), (mx, my) = self._axis(p1, p2, body)
        self.arrow((mx - 12, my + 12), (mx + 12, my - 12), size=5)

    def cap(self, p1, p2, gap=5, plate=16, polar=None):
        """polar: None, 'p1' (+ at p1 side) or 'p2' (+ at p2 side). Curved plate = - side."""
        a, b, (ux, uy), (mx, my) = self._axis(p1, p2, gap)
        self.line(p1, a)
        self.line(b, p2)
        nx, ny = -uy, ux
        h = plate / 2
        if polar is None:
            for q in (a, b):
                self.line((q[0] + nx * h, q[1] + ny * h), (q[0] - nx * h, q[1] - ny * h), w=1.6)
            return
        plus, minus, d = (a, b, 1) if polar == "p1" else (b, a, -1)
        self.line((plus[0] + nx * h, plus[1] + ny * h), (plus[0] - nx * h, plus[1] - ny * h), w=1.6)
        pts = []
        for i in range(13):
            t = -1 + i / 6
            off = 3.0 * t * t
            pts.append((minus[0] + nx * h * t + ux * d * off, minus[1] + ny * h * t + uy * d * off))
        self.line(*pts, w=1.6)
        # '+' sign beside the + plate, on the outside
        px = plus[0] - ux * d * 5 + nx * (h + 1)
        py = plus[1] - uy * d * 5 + ny * (h + 1)
        self.text(px, py + 3, "+", 8, "c", FONTB)

    def diode(self, p1, p2, size=9):
        """anode at p1, cathode at p2"""
        a, b, (ux, uy), (mx, my) = self._axis(p1, p2, size)
        self.line(p1, a)
        self.line(b, p2)
        nx, ny = -uy, ux
        h = size * 0.6
        p = self.c.beginPath()
        p.moveTo(self.X(a[0] + nx * h), self.Y(a[1] + ny * h))
        p.lineTo(self.X(a[0] - nx * h), self.Y(a[1] - ny * h))
        p.lineTo(self.X(b[0]), self.Y(b[1]))
        p.close()
        self.c.drawPath(p, stroke=1, fill=1)
        self.line((b[0] + nx * h, b[1] + ny * h), (b[0] - nx * h, b[1] - ny * h), w=1.6)

    def gnd(self, x, y, lead=8):
        self.line((x, y), (x, y + lead))
        y2 = y + lead
        for i, half in enumerate((8, 5, 2)):
            self.line((x - half, y2 + i * 3), (x + half, y2 + i * 3), w=1.3)

    def chassis(self, x, y, lead=8, width=18):
        self.line((x, y), (x, y + lead))
        y2 = y + lead
        self.line((x - width / 2, y2), (x + width / 2, y2), w=1.3)
        for i in range(4):
            xx = x - width / 2 + i * width / 3
            self.line((xx, y2), (xx - 4, y2 + 6))

    def opamp(self, xl, yc, name="", w=56, h=58, pins=None, inv_top=True, sz=8.5):
        """triangle pointing right. returns dict of pin coords:
        inv, non, out, top, bot (on triangle edges)."""
        xr = xl + w
        yt, yb = yc - h / 2, yc + h / 2
        self.line((xl, yt), (xl, yb), (xr, yc), (xl, yt), w=1.3)
        yi = yc - 12
        yn = yc + 12
        if not inv_top:
            yi, yn = yn, yi
        self.text(xl + 4, yi + 3.5, "−", 9, "l", FONTB)
        self.text(xl + 4, yn + 3.5, "+", 9, "l", FONTB)
        if name:
            self.text(xl + w * 0.46, yc + 3.5, name, sz, "c", FONTB)
        xm = xl + w * 0.42
        ytop = yt + (xm - xl) * (h / 2) / w
        ybot = yb - (xm - xl) * (h / 2) / w
        d = dict(inv=(xl, yi), non=(xl, yn), out=(xr, yc), top=(xm, ytop), bot=(xm, ybot))
        if pins:
            for k, v in pins.items():
                x, y = d[k]
                if k in ("inv", "non"):
                    self.text(x - 3, y - 2.5, str(v), 7.5, "r")
                elif k == "out":
                    self.text(x + 3, y - 4, str(v), 7.5, "l")
                elif k == "top":
                    self.text(x + 4, y - 2, str(v), 7.5, "l")
                else:
                    self.text(x + 4, y + 8, str(v), 7.5, "l")
        return d

    def bjt(self, bx, by, kind="npn", c_up=True, size=18):
        """base lead ends at (bx,by) where it meets the bar. Returns (c, e) end points."""
        bar = bx
        self.line((bar, by - 11), (bar, by + 11), w=2.2)
        dy = -1 if c_up else 1
        c0 = (bar, by + dy * 5)
        c1 = (bar + 14, by + dy * 16)
        e0 = (bar, by - dy * 5)
        e1 = (bar + 14, by - dy * 16)
        self.line(c0, c1)
        self.line(e0, e1)
        ang = math.degrees(math.atan2(e1[1] - e0[1], e1[0] - e0[0]))
        if kind == "npn":
            self.arrowhead(e0[0] + (e1[0] - e0[0]) * 0.85, e0[1] + (e1[1] - e0[1]) * 0.85, ang, 6)
        else:
            self.arrowhead(e0[0] + (e1[0] - e0[0]) * 0.25, e0[1] + (e1[1] - e0[1]) * 0.25, ang + 180, 6)
        return c1, e1

    def coil_h(self, x1, x2, y, n=6, up=True):
        w = (x2 - x1) / n
        r = w / 2
        for i in range(n):
            cx = x1 + w * i + r
            self._lw()
            p = self.c.beginPath()
            if up:
                p.arc(self.X(cx - r), self.Y(y + r), self.X(cx + r), self.Y(y - r), 0, 180)
            else:
                p.arc(self.X(cx - r), self.Y(y + r), self.X(cx + r), self.Y(y - r), 180, 180)
            self.c.drawPath(p, stroke=1, fill=0)

    def switch_spst(self, x, y1, y2):
        """vertical SPST between (x,y1) and (x,y2)"""
        self.ocircle(x, y1)
        self.ocircle(x, y2)
        self.line((x, y2 - 2.6), (x + 9, y1 + 4), w=1.3)

    def circA(self, x, y, r=5.5, sz=7.5):
        self._lw(0.9)
        self.c.circle(self.X(x), self.Y(y), r * self.s, stroke=1, fill=0)
        self.text(x, y + 2.7, "A", sz, "c", FONTB)
