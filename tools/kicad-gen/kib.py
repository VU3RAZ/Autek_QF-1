"""KiCad backend with the same drawing API as sch.S (the PDF redraw toolkit).
Geometry from the redraw is scaled by K (12 redraw units == 2.54 mm) and snapped
to the 1.27 mm grid; components become real KiCad symbols joined by wires."""
import re
from kisch import Sheet, pins_of
from xform import xform
from sexp import Sym

K = 2.54 / 12.0
G = 1.27
SENT = -10000.0          # sentinel coordinate: wires touching it are dropped


def snap(v):
    return round(round(v / G) * G, 4)


class KB:
    def __init__(self, sheet: Sheet, parts, ox=30.0, oy=20.0, pinmap=None, kx=1.0):
        self.sh, self.parts = sheet, parts
        self.KX = K * kx
        self.ox, self.oy = ox, oy
        self.pending = []          # unassigned parts waiting for a reference
        self.last_term = None
        self.last_arrow = None
        self.pinmap = pinmap or {}  # board pin label -> net
        self.placed_refs = set()
        self.c = None
        self.s = 1.0

    # ------------------------------------------------------------ coords
    def P(self, x, y):
        return (snap(self.ox + x * self.KX), snap(self.oy + y * K))

    def R(self, X, Y):
        """sheet mm -> redraw units (exact inverse for on-grid points)"""
        return ((X - self.ox) / self.KX, (Y - self.oy) / K)

    # ------------------------------------------------------------ wires
    def _seg(self, a, b):
        if a == b:
            return
        if a[0] != b[0] and a[1] != b[1]:          # non-orthogonal: dog-leg
            xm = snap((a[0] + b[0]) / 2)
            self.sh.wire(a, (xm, a[1]))
            self.sh.wire((xm, a[1]), (xm, b[1]))
            self.sh.wire((xm, b[1]), b)
        else:
            self.sh.wire(a, b)

    def wire(self, *pts, hops=()):
        if any(p[0] <= SENT / 2 or p[1] <= SENT / 2 for p in pts):
            return
        q = [self.P(*p) for p in pts]
        for a, b in zip(q[:-1], q[1:]):
            self._seg(a, b)

    def wire_mm(self, *q):
        for a, b in zip(q[:-1], q[1:]):
            self._seg(a, b)

    def line(self, *pts, **kw):
        pass

    def dot(self, x, y, r=None):
        X, Y = self.P(x, y)
        self.sh.items.append([Sym("junction"), [Sym("at"), X, Y], [Sym("diameter"), 0],
                              [Sym("color"), 0, 0, 0, 0], [Sym("uuid"), __import__("uuid").uuid4().__str__()]])

    def rect(self, x1, y1, x2, y2, w=None, dash=None):
        a, b = self.P(x1, y1), self.P(x2, y2)
        self.sh.rect(a[0], a[1], b[0], b[1])

    def ocircle(self, *a, **k):
        pass

    def arrowhead(self, *a, **k):
        pass

    def coil_h(self, *a, **k):
        pass

    # ------------------------------------------------------------ text / labels
    def term(self, x, y, lab=None):
        self.last_term = (x, y)

    def _edge_dir(self, x, y):
        X, Y = self.P(x, y)
        return X, Y

    def text(self, x, y, s, size=8, anchor="l", font=None, ital=False):
        s0 = s.split("\n")[0].strip()
        # terminal label right after term()
        if self.last_term is not None:
            tx, ty = self.last_term
            self.last_term = None
            if s0 in self.pinmap:
                self.attach_net(self.pinmap[s0], tx, ty)
                return
        # arrow end that names a supply
        if self.last_arrow is not None and s0 in ("B+", "GND"):
            (X, Y), d = self.last_arrow
            self.last_arrow = None
            self.sh.power(s0, X, Y, d)
            return
        m = re.match(r"^([RCDQ])(\d+)$", s0.split()[0] if s0 else "")
        if m:
            letter = m.group(1)
            for p in reversed(self.pending):
                if p["kind"][0].upper() == letter or (letter == "R" and p["kind"] == "trim"):
                    if p["kind"] == "cap" and letter != "C":
                        continue
                    self.pending.remove(p)
                    self.place(s0.split()[0], p)
                    return

    def attach_net(self, net, x, y):
        X, Y = self.P(x, y)
        if net in ("GND", "B+"):
            self.sh.power(net, X, Y, (0, 1) if net == "GND" else (0, -1))
            return
        ang = 0
        if abs(Y - self.P(0, self.BY2)[1]) < 0.01:
            ang = 270
        elif abs(Y - self.P(0, self.BY1)[1]) < 0.01:
            ang = 90
        elif abs(X - self.P(self.BX1, 0)[0]) < 0.01:
            ang = 180
        just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[ang]
        from kisch import eff, U
        self.sh.items.append([Sym("label"), net, [Sym("at"), X, Y, ang], [Sym("fields_autoplaced")],
                              eff(1.27, just), [Sym("uuid"), U()]])

    def arrow(self, *pts, size=6, w=None):
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        if x1 != x2 and y1 != y2:      # diagonal = annotation pointer
            return
        self.wire(*pts)
        d = (0 if x1 == x2 else (1 if x2 > x1 else -1), 0 if y1 == y2 else (1 if y2 > y1 else -1))
        self.last_arrow = (self.P(x2, y2), d)

    def circA(self, x, y, *a, **k):
        if self.last_arrow:
            (X, Y), d = self.last_arrow
            self.last_arrow = None
            self.sh.label("BIAS", X, Y, 0 if d[0] >= 0 else 180)

    def gnd(self, x, y, lead=8):
        X, Y = self.P(x, y)
        self.sh.power("GND", X, Y, (0, 1))

    def chassis(self, x, y, lead=8, width=18):
        self.gnd(x, y)

    # ------------------------------------------------------------ parts
    def res(self, p1, p2, body=30, **k):
        self.pending.append(dict(kind="res", a=p1, b=p2))
        return p1, p2

    def cap(self, p1, p2, gap=5, plate=16, polar=None):
        self.pending.append(dict(kind="cap", a=p1, b=p2, polar=polar))

    def trimpot(self, p1, p2, body=30):
        self.pending.append(dict(kind="trim", a=p1, b=p2))

    def diode(self, p1, p2, size=9):
        self.pending.append(dict(kind="dio", a=p1, b=p2))

    def pot(self, *a, **k):
        raise NotImplementedError

    def place(self, ref, p):
        part = self.parts[ref]
        a, b = self.P(*p["a"]), self.P(*p["b"])
        vert = a[0] == b[0]
        c = (snap((a[0] + b[0]) / 2), snap((a[1] + b[1]) / 2))
        kind = p["kind"]
        if kind == "res" or (kind == "cap" and not p.get("polar")):
            rot = 0 if vert else 90
        elif kind == "cap":
            plus_first = p["polar"] == "p1"          # + at a
            if vert:
                top_is_a = a[1] < b[1]
                rot = 0 if plus_first == top_is_a else 180
            else:
                left_is_a = a[0] < b[0]
                rot = 90 if plus_first == left_is_a else 270
        elif kind == "dio":                          # a = anode, b = cathode
            if vert:
                rot = 90 if b[1] > a[1] else 270
            else:
                rot = 0 if b[0] < a[0] else 180
        elif kind == "trim":
            rot = 90 if not vert else 0
        self._place_sym(ref, part, c, rot, None, 1)
        sym = self.sh.lib(part["sym"])
        pins = pins_of(sym)
        pos = {n: (round(c[0] + xform(px, py, rot)[0], 4), round(c[1] + xform(px, py, rot)[1], 4))
               for n, (u, px, py, ang, t) in pins.items()}
        ends = [n for n in pos if n in ("1", "2", "3")]
        if kind == "trim":
            e1, e3 = pos["1"], pos["3"]
            near_a = "1" if _d(e1, a) < _d(e3, a) else "3"
            far = "3" if near_a == "1" else "1"
            self.wire_mm(a, pos[near_a])
            self.wire_mm(b, pos[far])
            w = pos["2"]
            # wiper strapped to the pin on net INT3 (pin 3)
            corner = (pos["3"][0], w[1]) if not vert else (w[0], pos["3"][1])
            self.wire_mm(w, corner, pos["3"])
            return
        n1, n2 = "1", "2"
        if _d(pos[n1], a) + _d(pos[n2], b) <= _d(pos[n1], b) + _d(pos[n2], a):
            self.wire_mm(a, pos[n1])
            self.wire_mm(b, pos[n2])
        else:
            self.wire_mm(a, pos[n2])
            self.wire_mm(b, pos[n1])

    def _place_sym(self, ref, part, c, rot, mirror, unit):
        x, y = c
        if rot in (0, 180):
            ra, va = (x + 2.2, y - 0.6), (x + 2.2, y + 1.9)
        else:
            ra, va = (x - 2.4, y - 2.0), (x + 11.5, y - 2.0)
        s = self.sh._inst(part["sym"], ref, part["value"], x, y, unit, part["fp"],
                          [("Note", part["note"])] if part.get("note") else [],
                          part.get("dnp", False), ra, va,
                          pins=[n for n, v in pins_of(self.sh.lib(part["sym"])).items() if v[0] in (0, unit)],
                          rot=rot)
        if mirror:
            s.insert(3, [Sym("mirror"), Sym(mirror)])
        if rot in (90, 270):
            for e in s:
                if isinstance(e, list) and e and e[0] == "property" and e[1] in ("Reference", "Value"):
                    e[3][3] = 90
        self.placed_refs.add(ref)
        return s

    def opamp(self, xl, yc, name="", w=56, h=58, pins=None, inv_top=True, sz=8.5, mirror_single=False):
        nm = name.strip().split()[0]
        m = re.match(r"^(U\d+)([AB]?)$", nm)
        ref, unit = m.group(1), {"": 1, "A": 1, "B": 2}[m.group(2)]
        part = self.parts[ref]
        X = round(snap(self.ox + (xl + 26) * self.KX) + G, 4)
        Y = snap(self.oy + yc * K)
        mir = "x" if (part["sym"].endswith("TL072") or mirror_single) else None
        s = self._place_sym(ref, part, (X, Y), 0, mir, unit)
        if part["sym"].endswith("TL072"):
            s[[i for i, e in enumerate(s) if isinstance(e, list) and e[0] == "property" and e[1] == "Reference"][0]][3] = [Sym("at"), X + 1.0, Y - 5.6, 0]
        sym = self.sh.lib(part["sym"])
        pins = pins_of(sym)
        pp = {n: (round(X + xform(px, py, 0, mir)[0], 4), round(Y + xform(px, py, 0, mir)[1], 4))
              for n, (u, px, py, a, t) in pins.items() if u in (0, unit)}
        if part["sym"].endswith("TL072"):
            inv, non, out = ("2", "3", "1") if unit == 1 else ("6", "5", "7")
            res = dict(inv=self.R(*pp[inv]), non=self.R(*pp[non]), out=self.R(*pp[out]))
        elif mirror_single:
            res = dict(inv=self.R(*pp["2"]), non=self.R(*pp["3"]), out=self.R(*pp["6"]))
            v7, v4 = pp["7"], pp["4"]
            self.sh.wire(v7, (v7[0], v7[1] + 1.27))
            self.sh.power("B+", v7[0], v7[1] + 1.27, (0, 1))
            self.sh.wire(v4, (v4[0], v4[1] - 1.27))
            self.sh.power("GND", v4[0], v4[1] - 1.27, (0, -1))
            for n in ("1", "5"):
                self.sh.noconn(*pp[n])
        else:
            res = dict(inv=self.R(*pp["2"]), non=self.R(*pp["3"]), out=self.R(*pp["6"]),
                       top=self.R(*pp["7"]), bot=self.R(*pp["4"]))
            for n in ("1", "5"):
                self.sh.noconn(*pp[n])
        return res

    def bjt(self, bx, by, kind="npn", c_up=True, size=18):
        ref = self._next_q
        part = self.parts[ref]
        B = self.P(bx, by)
        X, Y = round(B[0] + 5.08, 4), B[1]
        mirror = None if c_up else "x"
        self._place_sym(ref, part, (X, Y), 0, mirror, 1)
        pins = pins_of(self.sh.lib(part["sym"]))
        pp = {n: (round(X + xform(px, py, 0, mirror)[0], 4), round(Y + xform(px, py, 0, mirror)[1], 4))
              for n, (u, px, py, a, t) in pins.items()}
        return self.R(*pp["1"]), self.R(*pp["3"])

    def finish(self):
        if self.pending:
            raise RuntimeError("unassigned parts: %r" % self.pending)


def _d(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1])
