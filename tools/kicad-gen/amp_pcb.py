import sys
import pcb
from paths import KOUT

NAME = "QF1_Amp_Supply"
OUT = f"{KOUT}/{NAME}"
W, H = 92, 64

# ref: (x, y, rotation)  -- R/D: rot 0 = pad1 left, pad2 +10.16 right; 270 = pad2 below
PL = {
    # connections
    "J102": (6.5, 31.24, 90),    # pin1 IN (bottom) .. pin4 B+ (top); wire entry faces left edge
    "J101": (85.5, 40, 270),     # AC1, AC2
    # Sallen-Key input + U101
    "R101": (13, 9, 0),
    "R102": (27, 9, 0),
    "C101": (27, 14, 0),
    "C102": (27, 27.5, 0),
    "U101": (42, 14, 0),
    "C109": (52, 31, 90),
    # driver / bias / output
    "R103": (52, 8, 0),
    "C103": (52, 3.8, 0),
    "R104": (63, 13, 270),
    "D101": (63, 36.16, 90),
    "R105": (57, 38, 270),
    "Q101": (68, 9, 0),
    "Q102": (68, 30, 0),
    "R106": (77.5, 3.5, 270),
    "R107": (77.5, 26, 270),
    "C104": (68, 20.5, 0),
    "R108": (13, 33, 0),
    "C105": (13, 38, 0),
    # supply
    "C106": (37, 49, 0),
    "D102": (66, 46, 0),
    "D103": (66, 50, 0),
    "D104": (66, 54, 0),
    "D105": (66, 58, 0),
    # holes
    "H101": (4, 4, 0), "H102": (88, 4, 0), "H103": (4, 60, 0), "H104": (88, 60, 0),
}
POWER = ["GND", "B+", "AC1", "AC2", "EMIT", "QC1", "QC2", "AUDIO_OUT"]
SILK = [
    ("QF-1 AUDIO PWR AMP / AC SUPPLY", 46, 61.3, 1.2, "F"),
    ("B+", 13.2, 16, 1.0, "F"), ("OUT", 13.8, 21.1, 1.0, "F"), ("GND", 13.8, 26.2, 1.0, "F"),
    ("IN", 13.2, 31.2, 1.0, "F"),
    ("12-15", 78.5, 38.2, 1.0, "F"), ("VAC", 78.5, 47.5, 1.0, "F"),
    ("RF GND", 4, 8.3, 0.9, "F"),
    ("TL071/BC337/BC327 (orig. uA741/MPS6560/6562)", 46, 2.0, 0.8, "B"),
]

if __name__ == "__main__":
    board, path = pcb.build(NAME, OUT, PL, (W, H), POWER, SILK, holes_gnd=("H101",),
                            ref_pos={"J102": (11, 36), "J101": (80, 50)},
                            title="Autek QF-1 — Audio Power Amp / Supply Board")
    print("placed", path)
    r = pcb.autoroute(board, path, passes=int(sys.argv[1]) if len(sys.argv) > 1 else 40)
    print("\n".join(l for l in r.stdout.splitlines() if "routing" in l.lower() or "complete" in l.lower())[-1500:])
    pcb.add_pours(board, W, H)
    import pcbnew
    pcbnew.SaveBoard(path, board)
    print("drc:", pcb.drc(board, path))
