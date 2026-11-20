"""Generate a KiCad 7 schematic (.kicad_sch) from a part/net description.
Every pin gets a short wire stub ending in a net label (or a power symbol for
GND / B+), so connectivity is explicit and ERC-checkable."""
import copy
import math
import uuid
from sexp import Sym, parse, dump, find, findall
from xform import xform

LIBDIR = "/usr/share/kicad/symbols"
_cache = {}


def U():
    return str(uuid.uuid4())


def lib_file(lib):
    if lib not in _cache:
        _cache[lib] = parse(open(f"{LIBDIR}/{lib}.kicad_sym").read())[0]
    return _cache[lib]


def raw_symbol(lib, name):
    for s in findall(lib_file(lib), Sym("symbol")):
        if s[1] == name:
            return s
    raise KeyError(f"{lib}:{name}")


def bplus_symbol():
    """project-local power symbol 'QF1:B+' (copy of power:VCC, pin renamed)"""
    s = copy.deepcopy(raw_symbol("power", "VCC"))
    txt = dump(s).replace('"VCC', '"B+').replace('(name "VCC"', '(name "B+"')
    s = parse(txt)[0]
    for p in findall(s, Sym("property")):
        if p[1] == "Value":
            p[2] = "B+"
        if p[1] == "ki_description":
            p[2] = "Power symbol creates a global label with name \"B+\""
    return s


def flat_symbol(lib, name):
    """symbol with 'extends' resolved, named 'lib:name' for lib_symbols"""
    if lib == "QF1" and name == "B+":
        s = bplus_symbol()
        s[1] = "QF1:B+"
        return s
    s = copy.deepcopy(raw_symbol(lib, name))
    ext = find(s, Sym("extends"))
    if ext:
        parent = copy.deepcopy(raw_symbol(lib, ext[1]))
        pname = ext[1]
        child_props = {p[1]: p for p in findall(s, Sym("property"))}
        out = [Sym("symbol"), name]
        for x in parent[2:]:
            if isinstance(x, list) and x[0] == "property":
                out.append(child_props.pop(x[1], x))
            elif isinstance(x, list) and x[0] == "symbol":
                x[1] = x[1].replace(pname + "_", name + "_", 1)
                out.append(x)
            else:
                out.append(x)
        for p in child_props.values():
            out.append(p)
        s = out
    s[1] = f"{lib}:{name}"
    return s


def pins_of(sym):
    """{pin_number: (unit, x, y, angle, type)} ; unit 0 = common to all units"""
    res = {}
    for sub in findall(sym, Sym("symbol")):
        parts = sub[1].rsplit("_", 2)
        unit = int(parts[-2])
        for p in findall(sub, Sym("pin")):
            at = find(p, Sym("at"))
            num = find(p, Sym("number"))[1]
            res[num] = (unit, float(at[1]), float(at[2]), float(at[3]), str(p[1]))
    return res


def unit_count(sym):
    return max([int(s[1].rsplit("_", 2)[-2]) for s in findall(sym, Sym("symbol"))] + [1])


def eff(size=1.27, justify=None, hide=False):
    e = [Sym("effects"), [Sym("font"), [Sym("size"), size, size]]]
    if justify:
        e.append([Sym("justify")] + [Sym(j) for j in justify.split()])
    if hide:
        e.append(Sym("hide"))
    return e


class Sheet:
    def __init__(self, project, title, paper="A3", rev="1.0", comments=()):
        self.project = project
        self.root = U()
        self.items = []
        self.libs = {}
        self.pwr_n = 0
        self.title = title
        self.paper = paper
        self.rev = rev
        self.comments = comments
        self.placed = {}   # ref -> list of (unit, X, Y)
        self.pin_pos = {}  # (ref, pin) -> (x, y)

    def lib(self, lib_id):
        if lib_id not in self.libs:
            lib, name = lib_id.split(":")
            self.libs[lib_id] = flat_symbol(lib, name)
        return self.libs[lib_id]

    # --------------------------------------------------------------- primitives
    def wire(self, a, b):
        self.items.append([Sym("wire"), [Sym("pts"), [Sym("xy"), a[0], a[1]], [Sym("xy"), b[0], b[1]]],
                           [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]],
                           [Sym("uuid"), U()]])

    def label(self, net, x, y, ang):
        just = "right bottom" if ang == 180 else "left bottom"
        self.items.append([Sym("label"), net, [Sym("at"), x, y, ang], [Sym("fields_autoplaced")],
                           eff(1.27, just), [Sym("uuid"), U()]])

    def noconn(self, x, y):
        self.items.append([Sym("no_connect"), [Sym("at"), x, y], [Sym("uuid"), U()]])

    def text(self, s, x, y, size=1.8, bold=False):
        e = [Sym("effects"), [Sym("font"), [Sym("size"), size, size]] + ([Sym("bold")] if bold else []),
             [Sym("justify"), Sym("left"), Sym("bottom")]]
        self.items.append([Sym("text"), s, [Sym("at"), x, y, 0], e, [Sym("uuid"), U()]])

    def rect(self, x1, y1, x2, y2):
        self.items.append([Sym("rectangle"), [Sym("start"), x1, y1], [Sym("end"), x2, y2],
                           [Sym("stroke"), [Sym("width"), 0.15], [Sym("type"), Sym("dash")]],
                           [Sym("fill"), [Sym("type"), Sym("none")]], [Sym("uuid"), U()]])

    def _inst(self, lib_id, ref, value, x, y, unit, fp="", props=(), dnp=False, ref_at=None,
              val_at=None, hide_ref=False, hide_val=False, pins=(), rot=0):
        self.lib(lib_id)
        ra = ref_at or (x + 3, y - 1.5)
        va = val_at or (x + 3, y + 1.5)
        s = [Sym("symbol"), [Sym("lib_id"), lib_id], [Sym("at"), x, y, rot], [Sym("unit"), unit],
             [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
             [Sym("dnp"), Sym("yes" if dnp else "no")], [Sym("uuid"), U()],
             [Sym("property"), "Reference", ref, [Sym("at"), ra[0], ra[1], 0],
              eff(1.27, "left", hide_ref)],
             [Sym("property"), "Value", value, [Sym("at"), va[0], va[1], 0], eff(1.27, "left", hide_val)],
             [Sym("property"), "Footprint", fp, [Sym("at"), x, y, 0], eff(1.27, None, True)],
             [Sym("property"), "Datasheet", "~", [Sym("at"), x, y, 0], eff(1.27, None, True)]]
        for k, v in props:
            s.append([Sym("property"), k, v, [Sym("at"), x, y, 0], eff(1.27, None, True)])
        for p in pins:
            s.append([Sym("pin"), p, [Sym("uuid"), U()]])
        s.append([Sym("instances"), [Sym("project"), self.project,
                                     [Sym("path"), "/" + self.root, [Sym("reference"), ref],
                                      [Sym("unit"), unit]]]])
        self.items.append(s)
        return s

    def power(self, kind, x, y, d=None):
        """kind 'GND' or 'B+' ; (x,y) = connection point; d = outward direction"""
        self.pwr_n += 1
        if kind == "GND":
            rot = {(0, 1): 0, (1, 0): 90, (-1, 0): 270, (0, -1): 180}[d or (0, 1)]
            off = {0: (0, 4.2), 90: (4.5, 0), 270: (-7.5, 0), 180: (0, -3)}[rot]
            self._inst("power:GND", f"#PWR{self.pwr_n:03d}", "GND", x, y, 1,
                       ref_at=(x, y + 6), val_at=(x + off[0] - 1.5, y + off[1]), hide_ref=True,
                       pins=["1"], rot=rot)
        else:
            rot = {(0, -1): 0, (-1, 0): 90, (1, 0): 270, (0, 1): 180}[d or (0, -1)]
            off = {0: (0, -3.6), 90: (-5.5, 0.5), 270: (3.2, 0.5), 180: (0, 5)}[rot]
            self._inst("QF1:B+", f"#PWR{self.pwr_n:03d}", "B+", x, y, 1,
                       ref_at=(x, y - 6), val_at=(x + off[0] - 1.0, y + off[1]), hide_ref=True,
                       pins=["1"], rot=rot)

    def pwr_flag(self, net, x, y):
        self.pwr_n += 1
        self._inst("power:PWR_FLAG", f"#FLG{self.pwr_n:03d}", "PWR_FLAG", x, y, 1,
                   ref_at=(x, y - 6), val_at=(x - 1, y - 4), hide_ref=True, pins=["1"])
        self.wire((x, y), (x, y + 2.54))
        self.connect(net, x, y + 2.54, (0, 1))

    def connect(self, net, x, y, d):
        """attach net at (x,y); d = outward direction unit vector"""
        if net in ("GND", "B+"):
            self.power(net, x, y, d)
        else:
            ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 0, (0, 1): 0}[d]
            self.label(net, x, y, ang)

    # --------------------------------------------------------------- parts
    def part(self, ref, p, x, y, unit=1, stub=2.54, ref_at=None, val_at=None):
        sym = self.lib(p["sym"])
        pins = pins_of(sym)
        props = []
        if p.get("note"):
            props.append(("Note", p["note"]))
        unit_pins = [n for n, v in pins.items() if v[0] in (0, unit)]
        self._inst(p["sym"], ref, p["value"], x, y, unit, p["fp"], props, p.get("dnp", False),
                   ref_at, val_at, pins=unit_pins)
        for num in unit_pins:
            u_, px, py, a, typ = pins[num]
            X, Y = round(x + px, 2), round(y - py, 2)
            self.pin_pos[(ref, num)] = (X, Y)
            # outward direction in sheet coords
            ox = -round(math.cos(math.radians(a)))
            oy = round(math.sin(math.radians(a)))
            d = (ox, oy)
            net = p["pins"].get(num)
            if net is None:
                if typ != "no_connect":
                    self.noconn(X, Y)
                continue
            ex, ey = round(X + ox * stub, 2), round(Y + oy * stub, 2)
            self.wire((X, Y), (ex, ey))
            self.connect(net, ex, ey, d)

    # --------------------------------------------------------------- output
    def _conn_points(self):
        pts = set()
        for it in self.items:
            h = it[0]
            if h == "wire":
                p = find(it, Sym("pts"))
                for xy in p[1:]:
                    pts.add((round(xy[1], 4), round(xy[2], 4)))
            elif h in ("junction", "label", "no_connect"):
                at = find(it, Sym("at"))
                pts.add((round(at[1], 4), round(at[2], 4)))
            elif h == "symbol":
                lib_id = find(it, Sym("lib_id"))[1]
                at = find(it, Sym("at"))
                unit = find(it, Sym("unit"))[1]
                mir = find(it, Sym("mirror"))
                mir = str(mir[1]) if mir else None
                for n, (u, px, py, a, t) in pins_of(self.lib(lib_id)).items():
                    if u in (0, unit):
                        dx, dy = xform(px, py, int(at[3]), mir)
                        pts.add((round(at[1] + dx, 4), round(at[2] + dy, 4)))
        return pts

    def split_wires(self):
        pts = self._conn_points()
        new = []
        for it in self.items:
            if it[0] != "wire":
                new.append(it)
                continue
            p = find(it, Sym("pts"))
            (x1, y1), (x2, y2) = (p[1][1], p[1][2]), (p[2][1], p[2][2])
            inner = []
            for (px, py) in pts:
                if x1 == x2 == px and min(y1, y2) < py < max(y1, y2):
                    inner.append((px, py))
                elif y1 == y2 == py and min(x1, x2) < px < max(x1, x2):
                    inner.append((px, py))
            if not inner:
                new.append(it)
                continue
            inner.sort(key=lambda q: abs(q[0] - x1) + abs(q[1] - y1))
            chain = [(x1, y1)] + inner + [(x2, y2)]
            for a, b in zip(chain[:-1], chain[1:]):
                new.append([Sym("wire"), [Sym("pts"), [Sym("xy"), a[0], a[1]], [Sym("xy"), b[0], b[1]]],
                            [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]],
                            [Sym("uuid"), U()]])
        self.items = new

    def save(self, path):
        self.split_wires()
        tb = [Sym("title_block"), [Sym("title"), self.title], [Sym("date"), "2026-11-19"],
              [Sym("rev"), self.rev], [Sym("company"), "Redrawn from Autek Research QF-1 manual"]]
        for i, c in enumerate(self.comments, 1):
            tb.append([Sym("comment"), i, c])
        doc = [Sym("kicad_sch"), [Sym("version"), Sym("20230121")], [Sym("generator"), Sym("eeschema")],
               [Sym("uuid"), self.root], [Sym("paper"), self.paper], tb,
               [Sym("lib_symbols")] + list(self.libs.values())]
        doc += self.items
        doc.append([Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]])
        open(path, "w").write(dump(doc) + "\n")
