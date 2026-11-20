import csv
from collections import OrderedDict
from design import MAIN, AMP
from paths import KOUT
for b in (MAIN, AMP):
    groups = OrderedDict()
    for ref, p in sorted(b["parts"].items(), key=lambda kv: (kv[0][0], int(''.join(c for c in kv[0] if c.isdigit()) or 0))):
        if ref.startswith("H") and p["sym"] == "Mechanical:MountingHole":
            continue
        key = (p["value"], p["fp"].split(":")[1], p.get("dnp", False), p.get("note", ""))
        groups.setdefault(key, []).append(ref)
    path = f"{KOUT}/{b['name']}/docs/{b['name']}-BOM.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Qty", "References", "Value", "Footprint", "Fit", "Notes"])
        for (val, fp, dnp, note), refs in groups.items():
            w.writerow([len(refs), " ".join(refs), val, fp, "DNP" if dnp else "fit", note])
    print(path, len(groups), "lines")
