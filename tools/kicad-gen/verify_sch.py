"""Export the netlist with kicad-cli (KiCad's own connectivity engine) and
compare it with the design netlist; also run basic ERC-style checks."""
import subprocess
import sys
from collections import defaultdict
from sexp import parse, find, findall, Sym
from design import MAIN, AMP
from paths import KOUT

OUT = KOUT
ok_all = True
for b in [x for x in (MAIN, AMP) if len(sys.argv) < 2 or x["name"] in sys.argv[1:]]:
    n = b["name"]
    sch = f"{OUT}/{n}/{n}.kicad_sch"
    net = f"{OUT}/{n}/{n}.net"
    r = subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", net, sch],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(1)
    e = parse(open(net).read())[0]
    got = {}
    pintypes = {}
    for nn in findall(find(e, Sym("nets")), Sym("net")):
        name = find(nn, Sym("name"))[1].lstrip("/")
        nodes = set()
        for nd in findall(nn, Sym("node")):
            ref = find(nd, Sym("ref"))[1]
            pin = find(nd, Sym("pin"))[1]
            pt = find(nd, Sym("pintype"))
            if ref.startswith("#"):
                continue
            nodes.add((ref, pin))
            pintypes[(ref, pin)] = pt[1] if pt else "?"
        if nodes:
            got[name] = frozenset(nodes)
    swap = {r for r, p in b["parts"].items() if p["sym"] in ("Device:R", "Device:C")}
    canon = lambda s_: frozenset((r, "*" if r in swap else pn) for r, pn in s_)
    rawgot = dict(got)
    got = {k: canon(v) for k, v in got.items()}
    want = defaultdict(set)
    for ref, p in b["parts"].items():
        for pin, nt in p["pins"].items():
            want[nt].add((ref, pin))
    want = {k: canon(v) for k, v in want.items()}
    # compare as partitions (names may differ only for unconnected-* nets)
    gs = set(v for v in got.values())
    ws = set(want.values())
    missing = ws - gs
    extra = gs - ws
    # name check
    namebad = [k for k, v in want.items() if got.get(k) != v]
    print(f"== {n}: {len(want)} design nets, {len(got)} netlist nets")
    unconn = [k for k, v in got.items() if k.startswith("unconnected") or "unconnected" in k]
    single = [k for k, v in got.items() if len(v) == 1 and not k.startswith("unconnected")]
    print("   partition mismatch:", len(missing), len(extra))
    for m in missing:
        print("     want", sorted(m))
    for m in extra:
        if not any("unconnected" in k for k, v in got.items() if v == m):
            print("     got ", sorted(m))
    print("   name mismatches:", namebad)
    print("   single-pin nets:", single)
    # unconnected-pin check: any connected pins of parts not in design?
    nc = [k for k in got if "unconnected" in k]
    print("   pins flagged no-connect / unconnected:", len(nc))
    # power-input driven check
    for k, v in rawgot.items():
        types = {pintypes[x] for x in v}
        if "power_in" in types and not types & {"power_out"} and k not in ("GND", "B+"):
            print("   WARNING power_in net without driver:", k)
    ok_all &= not missing and not namebad
print("ALL OK" if ok_all else "PROBLEMS")
