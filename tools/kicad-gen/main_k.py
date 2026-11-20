import sys
from paths import REDRAW
sys.path.insert(0, REDRAW)
from kisch import Sheet
from kib import KB
from design import MAIN
import mainboard
from gen_sch import group
from paths import KOUT


def build_main_wired():
    P = MAIN["parts"]
    sh = Sheet(MAIN["name"], MAIN["title"], comments=(
        "U1-U3 TL072 replace uA747 (A/B halves keep the original U1A..U3B roles); U4 TL071 replaces uA741",
        "J1-J4 keep the original board pin numbers 1-21 (J2 pin n = board pin n+7). Dashed box = chassis boundary",
        "R3,R5,R10,R11 3.3K-6.8K matched to C2-C5 (1%); R4,R9 select to match selectivity pot",
        "C9, C10 values not given on original (optional, DNP); C7 not used in QF-1 (DNP)"))
    pinmap = {}
    for jref, base in (("J1", 0), ("J2", 7)):
        for pin, net in P[jref]["pins"].items():
            pinmap[str(int(pin) + base)] = net
    pinmap["20"] = "GND"
    pinmap["21"] = "OUT_QF1"
    kb = KB(sh, P, ox=22.0, oy=30.0, pinmap=pinmap, kx=1.33)
    kb.BX1, kb.BY1, kb.BX2, kb.BY2 = mainboard.BX1, mainboard.BY1, mainboard.BX2, mainboard.BY2
    mainboard.draw_main(None, 0, 0, 1, d=kb)
    kb.finish()
    for net, (x, y) in {"HP1": (225, 335), "SUM1": (130, 300), "INT1": (285, 360), "INT2": (392, 360),
                        "SUM2": (535, 300), "HP2": (640, 335), "INT3": (712, 360), "INT4": (860, 360),
                        "LP2": (950, 404), "U4_INV": (800, 94), "U4_OUT": (895, 125),
                        "C1_R1": (90, 305)}.items():
        X, Y = kb.P(x, y)
        sh.label(net, X, Y, 0)
    sh.text("QF FILTER — MAIN BOARD (wired from the original schematic)", 22, 22, 2.5, bold=True)
    # side blocks (label-connected)
    group(sh, P, "Board connections (original pin numbers)", 22, 168, 150, ["J1", "J2", "J3", "J4"])
    group(sh, P, "Op-amp power (U1-U3) and added decoupling", 177, 168, 140,
          [("U1", 3), ("U2", 3), ("U3", 3), "C13", "C14", "C15"])
    sh.pwr_flag("B+", 299.72, 175.26)
    sh.pwr_flag("GND", 307.34, 175.26)
    group(sh, P, "Mounting holes", 322, 168, 85, ["H1", "H2", "H3", "H4"])
    notes = ("FRONT-PANEL WIRING (as original):\n"
             "  5+6 tied -> front SELECTIVITY wiper; 8 -> top of front SELECTIVITY and front FREQUENCY wiper\n"
             "  9 -> top of front FREQUENCY;  13+16 tied -> rear SELECTIVITY wiper\n"
             "  18 -> top of rear SELECTIVITY and rear FREQUENCY wiper;  15 -> top of rear FREQUENCY\n"
             "  Pots: dual 500K (front/rear), bottom terminals open\n"
             "  Switch pole 1: common 12, PK 5, NTCH 10, LP 11\n"
             "  Switch pole 2: common 3,  PK 19, NTCH 17, LP 14\n"
             "  21 = QF-1 output to amp board IN;  20 = ground;  1 = B+ from amp board\n"
             "SUBSTITUTIONS / ADDITIONS: TL072 for uA747, TL071 for uA741; C13-C15 supply decoupling added")
    sh.text(notes, 22, 250, 1.6)
    return sh


if __name__ == "__main__":
    sh = build_main_wired()
    d = f"{KOUT}/{MAIN['name']}"
    sh.save(f"{d}/{MAIN['name']}.kicad_sch")
    print("ok")
