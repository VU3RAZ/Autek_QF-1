import os
os.environ.setdefault("KICAD7_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
import pcbnew
from collections import defaultdict
from design import MAIN, AMP
from paths import KOUT
for b in (MAIN, AMP):
    n = b["name"]
    brd = pcbnew.LoadBoard(f"{KOUT}/{n}/{n}.kicad_pcb")
    swap = {r for r, p in b["parts"].items() if p["sym"] in ("Device:R", "Device:C")}
    got = defaultdict(set)
    for fp in brd.GetFootprints():
        r = fp.GetReference()
        for pad in fp.Pads():
            if pad.GetNetname() and not pad.GetNetname().startswith("unconnected-"):
                got[pad.GetNetname()].add((r, "*" if r in swap else pad.GetNumber()))
    want = defaultdict(set)
    for r, p in b["parts"].items():
        for pin, net in p["pins"].items():
            want[net].add((r, "*" if r in swap else pin))
    ok = {frozenset(v) for v in got.values()} == {frozenset(v) for v in want.values()}
    tracks = sum(1 for t in brd.GetTracks() if t.GetClass() == "PCB_TRACK")
    bb = brd.GetBoardEdgesBoundingBox()
    print(f"{n}: pads-vs-original-netlist {'MATCH' if ok else 'MISMATCH'}; {len(brd.GetFootprints())} footprints, "
          f"{tracks} track segments, board {pcbnew.ToMM(bb.GetWidth()):.0f} x {pcbnew.ToMM(bb.GetHeight()):.0f} mm")
