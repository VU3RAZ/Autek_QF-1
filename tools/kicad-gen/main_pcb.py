import sys
import pcb
import pcbnew
from paths import KOUT

NAME = "QF1_Main_Filter"
OUT = f"{KOUT}/{NAME}"
W, H = 114, 84

V = 270   # vertical resistor: pad1 at (x,y), pad2 10.16 below
PL = {
    # connectors: original board numbering on the silkscreen
    "J1": (12, 79, 90),          # board pins 1..7, left to right
    "J2": (44, 79, 90),          # board pins 8..19
    "J3": (57, 5, 0),            # pin 20 GND
    "J4": (106, 9, 0),           # pin 21 QF-1 out
    # supply / bias
    "D1": (9, 6, 0),
    "R21": (24, 4, V), "R20": (28, 4, V),
    "C12": (32, 9, 0), "C13": (39.5, 9, 0),
    "C14": (24, 21, 0), "C15": (93, 22, 0),
    # output amplifier U4
    "U4": (78, 6, 0),
    "C11": (64, 7, 0), "R25": (64, 14, 0), "C6": (64, 19, 0),
    "R26": (92, 4, 0), "C7": (95, 15, 0),
    # op-amps
    "U1": (12, 34, 0), "U2": (46, 34, 0), "U3": (82, 34, 0),
    # integrator caps
    "C2": (22, 29, 0), "C3": (33, 29, 0), "C4": (91, 29, 0), "C5": (101, 29, 0),
    # section 1 resistors (vertical row)
    "C1": (4, 52, V), "R1": (8.5, 50, V), "R2": (12, 50, V), "R17": (15.5, 50, V), "C9": (19, 52, V),
    "R16": (22.5, 50, V), "R15": (26, 50, V), "R3": (29.5, 50, V), "R4": (33, 50, V), "R5": (36.5, 50, V),
    # section 2 resistors
    "R6": (44, 50, V), "R7": (47.5, 50, V), "R14": (51, 50, V), "C10": (54.5, 52, V),
    "R13": (58, 50, V), "R12": (61.5, 50, V), "R24": (68, 50, V), "R9": (71.5, 50, V),
    "R10": (75, 50, V), "R11": (78.5, 50, V), "R8": (88, 56, 0),
    # holes
    "H1": (3.5, 3.5, 0), "H2": (W - 3.5, 3.5, 0), "H3": (3.5, H - 3.5, 0), "H4": (W - 3.5, H - 3.5, 0),
}
POWER = ["GND", "B+", "B+IN"]
SILK = [("QF-1 MAIN FILTER BOARD", 92, 68, 1.4, "F"),
        ("Redrawn from Autek QF-1 manual - TL072 x3 (orig. uA747), TL071 (orig. uA741)", 57, 66, 0.9, "B")]
# original board pin numbers under J1 / J2
for i in range(7):
    SILK.append((str(i + 1), 12 + i * 2.54, 76.0, 0.9, "F"))
for i in range(12):
    SILK.append((str(i + 8), 44 + i * 2.54, 76.0, 0.9, "F"))
SILK += [("B+ OUT  .  IN SEL  .  GND", 19.6, 82, 0.8, "F"),
         ("20 GND", 57, 8.3, 0.9, "F"), ("21 OUT", 106, 12.3, 0.9, "F")]

if __name__ == "__main__":
    board, path = pcb.build(NAME, OUT, PL, (W, H), POWER, SILK,
                            title="Autek QF-1 — Main Filter Board",
                            ref_pos={"J1": (5.5, 79), "J2": (37.5, 79), "J3": (61, 5), "J4": (110, 9)})
    print("placed", path)
    if len(sys.argv) > 1 and sys.argv[1] == "place":
        sys.exit()
    r = pcb.autoroute(board, path, passes=60)
    pcb.add_pours(board, W, H)
    pcbnew.SaveBoard(path, board)
    print("drc:", pcb.drc(board, path))
