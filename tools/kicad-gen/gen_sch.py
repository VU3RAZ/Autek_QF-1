import os
import sys
from kisch import Sheet, pins_of, bplus_symbol
from sexp import Sym, dump
from design import MAIN, AMP
from paths import KOUT

OUTDIR = KOUT

# cell (width, height, origin offset x, origin offset y)
def cell_for(sym, unit):
    if sym in ("Device:R", "Device:C", "Device:C_Polarized"):
        return 21, 24, 7, 11
    if sym == "Device:R_Potentiometer_Trim":
        return 30, 24, 7, 11
    if sym == "Device:D":
        return 38, 14, 18, 6
    if sym.startswith("Amplifier_Operational"):
        if unit == 3 or (sym.endswith("TL071") and False):
            return 22, 30, 8, 14
        return 52, 24, 24, 11
    if sym.startswith("Transistor_BJT"):
        return 38, 24, 18, 11
    if sym.startswith("Connector"):
        return 34, 0, 26, 6
    if sym.startswith("Mechanical"):
        return 22, 14, 6, 6
    raise KeyError(sym)


def group(sh, parts, title, x0, y0, w, items, h=None):
    x, y, rowh = x0 + 3, y0 + 10, 0
    for it in items:
        ref, unit = it if isinstance(it, tuple) else (it, 1)
        p = parts[ref]
        cw, chh, ox, oy = cell_for(p["sym"], unit)
        if p["sym"].startswith("Connector"):
            n = len(pins_of(sh.lib(p["sym"])))
            chh = n * 2.54 + 10
            oy = n * 1.27 + 4
        if x + cw > x0 + w:
            x, y, rowh = x0 + 3, y + rowh, 0
        X = round((x + ox) / 1.27) * 1.27
        Y = round((y + oy) / 1.27) * 1.27
        sh.part(ref, p, round(X, 2), round(Y, 2), unit)
        x += cw
        rowh = max(rowh, chh)
    hh = h or (y + rowh - y0 + 2)
    sh.rect(x0, y0, x0 + w, y0 + hh)
    sh.text(title, x0 + 2, y0 + 5, 2.0, bold=True)
    return y0 + hh


def build_main():
    P = MAIN["parts"]
    sh = Sheet(MAIN["name"], MAIN["title"], comments=(
        "U1-U3 TL072 replace uA747 (A/B halves keep original U1A..U3B roles); U4 TL071 replaces uA741",
        "J1/J2/J3/J4 pins keep original board numbering 1-21 (J2 pin n = board pin n+7)",
        "R3,R5,R10,R11 3.3K-6.8K matched to C2-C5 (1%); R4,R9 select to match selectivity pot",
        "C9, C10 values not given on original (fitted optional, DNP); C7 not used in QF-1 (DNP)"))
    group(sh, P, "Board connections (original pin numbers)", 15, 15, 75,
          ["J1", "J2", "J3", "J4"])
    group(sh, P, "Supply, bias (B+/2) and op-amp power", 95, 15, 160,
          ["D1", "R21", "R20", "C12", "C13", "C14", "C15", ("U1", 3), ("U2", 3), ("U3", 3)])
    sh.pwr_flag("B+", 240, 30)
    sh.pwr_flag("GND", 247.65, 30)
    group(sh, P, "Output amplifier U4 (feeds board pin 21)", 260, 15, 145,
          ["C11", "R25", "C6", "R26", "C7", "U4"])
    group(sh, P, "Filter section 1 — U1A summer, U1B / U2A integrators (HP1, BP1, LP1, notch1 = HP1+LP1)",
          95, 80, 310,
          [("U1", 1), ("U1", 2), ("U2", 1), "C1", "R1", "R2", "R17", "C9", "R16", "R15", "R3", "C2",
           "R4", "R5", "C3"])
    group(sh, P, "Filter section 2 — U2B summer, U3A / U3B integrators (HP2, BP2, LP2, notch2 = HP2+LP2)",
          95, 165, 310,
          [("U2", 2), ("U3", 1), ("U3", 2), "R6", "R7", "R14", "C10", "R13", "R12", "R8", "C4", "R24",
           "R9", "R10", "C5", "R11"])
    group(sh, P, "Mounting", 15, 120, 75, ["H1", "H2", "H3"])
    group(sh, P, "", 15, 150, 75, ["H4"])
    notes = ("NOTES\n"
             "Front panel wiring (unchanged from original):\n"
             " 5+6 tied -> front SELECTIVITY wiper; 8 -> top of front SELECTIVITY\n"
             "   and front FREQUENCY wiper; 9 -> top of front FREQUENCY\n"
             " 13+16 tied -> rear SELECTIVITY wiper; 18 -> top of rear SELECTIVITY\n"
             "   and rear FREQUENCY wiper; 15 -> top of rear FREQUENCY\n"
             " Pots: dual 500K, bottom terminals open\n"
             " Switch pole 1: com 12; PK 5; NTCH 10; LP 11\n"
             " Switch pole 2: com 3;  PK 19; NTCH 17; LP 14\n"
             " 21 = QF-1 output to amp board IN; 20 = gnd; 1 = B+ from amp board\n"
             "Added parts (not on original): C13, C14, C15 decoupling")
    sh.text(notes, 15, 190, 1.5)
    return sh


def build_amp():
    A = AMP["parts"]
    sh = Sheet(AMP["name"], AMP["title"], paper="A4", comments=(
        "U101 TL071 replaces uA741; Q101/Q102 BC337/BC327 replace MPS6560/MPS6562",
        "Mains transformer, switch and line caps are off-board; bridge D102-D105 accepts 12-15 VAC",
        "(original: centre-tapped secondary with 2 diodes). H101 pad = RF ground to chassis screw",
        "Sallen-Key low-pass (R101/R102/C101/C102) + complementary emitter-follower output"))
    group(sh, A, "AC input, rectifier, filter", 12, 15, 135,
          ["J101", "D102", "D103", "D104", "D105", "C106", "C109"])
    sh.pwr_flag("B+", 126, 52)
    sh.pwr_flag("GND", 133.35, 52)
    group(sh, A, "Connections to main board / panel", 152, 15, 130, ["J102", "H101", "H102", "H103", "H104"])
    group(sh, A, "Sallen-Key low-pass driver U101", 12, 82, 135,
          [("U101", 1), "R101", "R102", "C101", "C102"])
    group(sh, A, "Output stage", 152, 82, 130,
          ["Q101", "Q102", "R103", "C103", "R104", "D101", "R105", "R106", "R107", "C104", "R108", "C105"])
    return sh


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    for b, fn in ((MAIN, build_main), (AMP, build_amp)):
        d = f"{OUTDIR}/{b['name']}"
        os.makedirs(d, exist_ok=True)
        sh = fn()
        sh.save(f"{d}/{b['name']}.kicad_sch")
        bs = bplus_symbol()
        lib = [Sym("kicad_symbol_lib"), [Sym("version"), Sym("20220914")], [Sym("generator"), Sym("kicad_symbol_editor")], bs]
        open(f"{d}/QF1.kicad_sym", "w").write(dump(lib) + "\n")
        open(f"{d}/sym-lib-table", "w").write(
            '(sym_lib_table\n  (lib (name "QF1")(type "KiCad")(uri "${KIPRJMOD}/QF1.kicad_sym")(options "")(descr "Project power symbols"))\n)\n')
        print("wrote", b["name"])
