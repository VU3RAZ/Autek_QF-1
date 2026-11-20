#!/usr/bin/env python3
"""Turn the QF-1 SPICE netlists (*.cir) into LTspice schematics (*.asc).

Pin positions are read from YOUR LTspice installation's symbol files (.asy), so the
schematic matches your LTspice exactly. Each pin gets a short wire and a net label
(FLAG); parts are grouped by the "* ---- section" headings of the netlist. Directives
(.include/.param/.ac/.tran/.step/.meas) are placed on the sheet.

After writing each .asc, the script asks LTspice to netlist it (LTspice -netlist)
and checks that every connection matches the original .cir.

Usage:
    python make_asc.py                      # all *.cir here, auto-find LTspice
    python make_asc.py --sym "C:/Users/me/AppData/Local/LTspice/lib/sym" --exe "C:/Program Files/ADI/LTspice/LTspice.exe"
"""
import argparse
import glob
import os
import platform
import re
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

SYM_DIRS = [
    os.path.expandvars(r"%LOCALAPPDATA%\LTspice\lib\sym"),
    os.path.expanduser(r"~\Documents\LTspiceXVII\lib\sym"),
    r"C:\Program Files\LTC\LTspiceXVII\lib\sym",
    os.path.expanduser("~/Library/Application Support/LTspice/lib/sym"),
    os.path.expanduser("~/.wine/drive_c/users/%s/AppData/Local/LTspice/lib/sym" % os.environ.get("USER", "")),
    os.path.expanduser("~/.wine/drive_c/users/%s/Documents/LTspiceXVII/lib/sym" % os.environ.get("USER", "")),
]
EXES = [
    r"C:\Program Files\ADI\LTspice\LTspice.exe",
    r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe"),
    "/Applications/LTspice.app/Contents/MacOS/LTspice",
]

# netlist element -> LTspice symbol (relative to lib/sym)
SYMBOL_FOR = {"R": "res", "C": "cap", "CP": "polcap", "D": "diode", "QN": "npn", "QP": "pnp",
              "X": "Opamps/opamp2", "V": "voltage"}


def find_first(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def read_asy(symdir, name):
    path = os.path.join(symdir, *name.split("/")) + ".asy"
    if not os.path.exists(path):
        sys.exit(f"symbol not found: {path}")
    txt = open(path, encoding="latin-1").read().replace("\r", "")
    pins = []          # (x, y, spice_order)
    cur = None
    for ln in txt.split("\n"):
        t = ln.split()
        if not t:
            continue
        if t[0] == "PIN":
            cur = [int(t[1]), int(t[2]), None]
            pins.append(cur)
        elif t[0] == "PINATTR" and t[1] == "SpiceOrder" and cur is not None:
            cur[2] = int(t[2])
    if any(p[2] is None for p in pins):
        sys.exit(f"{path}: a PIN has no SpiceOrder")
    return {p[2]: (p[0], p[1]) for p in pins}


def parse_cir(path):
    """returns (title, groups[(name, [elements])], directives[str], nets{elem: [nodes]})"""
    lines = open(path).read().replace("\r", "").split("\n")
    title = lines[0].lstrip("* ").strip()
    groups, directives = [], []
    cur = ("Circuit", [])
    groups.append(cur)
    for ln in lines[1:]:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("* ----"):
            cur = (s[6:].strip(), [])
            groups.append(cur)
            continue
        if s.startswith("*."):
            directives.append(";" + s[1:])          # commented directive -> comment text
            continue
        if s.startswith("*"):
            continue
        if s.startswith("."):
            if s.lower().startswith(".end"):
                continue
            directives.append("!" + s)
            continue
        cur[1].append(s)
    return title, [g for g in groups if g[1]], directives


def element(line):
    t = line.split()
    name = t[0]
    k = name[0].upper()
    if k in "RCD":
        nodes, rest = t[1:3], t[3:]
        val = " ".join(rest)
        if k == "C" and re.match(r"^[\d.]+u", val) and float(re.match(r"^[\d.]+", val).group()) >= 1:
            k = "CP"
        return name, k, nodes, val, ""
    if k == "Q":
        model = t[4]
        kind = "QP" if re.search(r"327|PNP|557|3906", model, re.I) else "QN"
        return name, kind, t[1:4], model, ""
    if k == "X":
        # X name n1..n5 SUBCKT params
        nodes = t[1:6]
        return name, "X", nodes, t[6], " ".join(t[7:])
    if k == "V":
        return name, "V", t[1:3], " ".join(t[3:]), ""
    raise ValueError("unsupported element: " + line)


def build_asc(cir, symdir):
    title, groups, directives = parse_cir(cir)
    syms = {}
    out = ["Version 4", "SHEET 1 3600 2400"]
    expected = defaultdict(set)   # node -> {(name, order)}
    x0, y = 64, 96
    out.append(f"TEXT {x0} 32 Left 3 ;{title}")
    for gname, elems in groups:
        out.append(f"TEXT {x0} {y} Left 2 ;{gname}")
        y += 64
        x = x0 + 64
        row_h = 0
        for line in elems:
            name, kind, nodes, val, extra = element(line)
            symname = SYMBOL_FOR[kind]
            if symname not in syms:
                syms[symname] = read_asy(symdir, symname)
            pins = syms[symname]
            xs = [p[0] for p in pins.values()]
            ys = [p[1] for p in pins.values()]
            w = max(xs) - min(xs) + 288
            h = max(ys) - min(ys) + 160
            if x + w > 3400:
                x, y, row_h = x0 + 64, y + row_h, 0
            sx, sy = x - min(xs) + 112, y - min(ys) + 64
            out.append(f"SYMBOL {symname.replace('/', chr(92))} {sx} {sy} R0")
            out.append(f"SYMATTR InstName {name}")
            out.append(f"SYMATTR Value {val}")
            if extra:
                out.append(f"SYMATTR SpiceLine {extra}")
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            for order, node in enumerate(nodes, 1):
                px, py = pins[order]
                dx, dy = px - cx, py - cy
                if abs(dx) >= abs(dy):
                    ox, oy = (32 if dx > 0 else -32), 0
                else:
                    ox, oy = 0, (32 if dy > 0 else -32)
                ax, ay = sx + px, sy + py
                bx, by = ax + ox, ay + oy
                out.append(f"WIRE {ax} {ay} {bx} {by}")
                out.append(f"FLAG {bx} {by} {node}")
                expected[node.upper()].add((name.upper(), order))
            x += w
            row_h = max(row_h, h)
        y += row_h + 32
    for d in directives:
        out.append(f"TEXT {x0} {y} Left 2 {d}")
        y += 40
    out[1] = f"SHEET 1 3600 {y + 160}"
    asc = os.path.splitext(cir)[0] + ".asc"
    open(asc, "w", encoding="ascii", newline="\r\n").write("\n".join(out) + "\n")
    return asc, expected


def check_with_ltspice(exe, asc, expected):
    """netlist the .asc with LTspice and compare node membership"""
    net = os.path.splitext(asc)[0] + ".net"
    if os.path.exists(net):
        os.remove(net)
    cmd = [exe, "-netlist", asc]
    if platform.system() != "Windows" and exe.lower().endswith(".exe"):
        cmd = ["wine"] + cmd
    subprocess.run(cmd, timeout=120)
    if not os.path.exists(net):
        return f"LTspice did not write {net}; open the .asc once in LTspice and run it instead."
    got = defaultdict(set)
    for ln in open(net, encoding="latin-1").read().replace("\r", "").split("\n"):
        t = ln.split()
        if not t or t[0][0] in "*.;+":
            continue
        name = t[0].upper()
        k = name[0]
        n = 2 if k in "RCDV" else 3 if k == "Q" else 5 if k == "X" else 0
        for order, node in enumerate(t[1:1 + n], 1):
            got[node.upper()].add((name, order))
    bad = []
    for node, members in expected.items():
        if got.get(node) != members:
            bad.append((node, sorted(members), sorted(got.get(node, []))))
    if bad:
        return "MISMATCH:\n" + "\n".join(f"  {n}: expected {e} got {g}" for n, e, g in bad)
    return "connectivity matches the .cir"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sym", help="LTspice lib/sym directory")
    ap.add_argument("--exe", help="LTspice executable (for the -netlist check)")
    ap.add_argument("cir", nargs="*", help="netlists (default: all *.cir next to this script)")
    a = ap.parse_args()
    symdir = a.sym or find_first(SYM_DIRS)
    if not symdir:
        sys.exit("LTspice symbol folder not found; pass --sym <...>/lib/sym")
    exe = a.exe or find_first(EXES)
    files = a.cir or sorted(glob.glob(os.path.join(HERE, "*.cir")))
    for cir in files:
        asc, expected = build_asc(cir, symdir)
        msg = check_with_ltspice(exe, asc, expected) if exe else "LTspice not found: skipped check (pass --exe)"
        print(f"{os.path.basename(asc)}: {msg}")


if __name__ == "__main__":
    main()
