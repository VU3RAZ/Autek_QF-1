# CLAUDE.md: Autek QF-1 project

Context for Claude Code working in this repo.

## What this is
A rebuild of the Autek QF-1 audio filter (1970s ham-radio accessory), from the original manual scan
(https://vtda.org/docs/radio/Autek/Autek_QF-1.pdf). It has three parts:
1. `docs/Autek_QF-1_Instructions_Redrawn.pdf`: the manual, transcribed, with vector redraws of every drawing.
2. `kicad/`: two KiCad 7 projects (main filter board, amp/supply board), wired schematics plus routed PCBs.
3. `docs/QF1_How_It_Works.md`: circuit analysis and performance rating.

## Source of truth
- `tools/kicad-gen/design.py` holds the **netlist of both boards as traced from the original schematic**: parts, values,
  footprints and pin→net maps. Substitutions are in the `note` fields: TL072 for µA747, TL071 for µA741,
  BC337/BC327 for MPS6560/6562, bridge rectifier, and off-board mains.
- `tools/redraw/mainboard.py` and `amp.py` hold the drawing geometry of the original schematics. The KiCad main-board
  schematic is generated from the *same* geometry through a KiCad backend (`tools/kicad-gen/kib.py`), so it looks
  like the original. The amp schematic is drawn in `amp_k.py` with the supply section changed.

## Pipeline (run from `tools/kicad-gen/`)
```
python3 main_k.py && python3 amp_k.py   # write kicad/*/*.kicad_sch (wired schematics)
python3 verify_sch.py                   # kicad-cli exports the netlist -> compared net-by-net with design.py
python3 main_pcb.py && python3 amp_pcb.py   # place, Freerouting autoroute, GND pours, DRC report
python3 bom.py && python3 final_check.py    # BOM CSVs; every PCB pad's net vs design.py
```
Then export fab files with `kicad-cli pcb export gerbers|drill|pdf` and `kicad-cli sch export pdf`.
PDF redraw of the manual: `python3 tools/redraw/build.py` (needs reportlab and Liberation fonts).

Requirements: KiCad 7 (`pcbnew` Python module and `kicad-cli`), Java plus `xvfb-run` for Freerouting 1.9
(download https://github.com/freerouting/freerouting/releases/download/v1.9.0/freerouting-1.9.0.jar to `tools/`, or set `FREEROUTING_JAR`). Set `KICAD7_FOOTPRINT_DIR` if the
library tables aren't configured. All paths are repo-relative (`tools/kicad-gen/paths.py`).

## Gotchas
- **Re-running `main_k.py` / `amp_k.py` mints new symbol UUIDs.** The committed PCBs link to the committed
  schematics' UUIDs. After regenerating schematics, either rebuild the PCBs with the pipeline, or open the
  project in KiCad and run *Tools > Update PCB from Schematic* to keep the hand-checked routing.
- `kisch.Sheet.save()` splits wires at T-junctions. KiCad only connects a wire end to the middle of another
  wire if that wire is split there. Don't remove that step.
- Op-amp units of the TL072 are mirrored (− input on top, as in the original drawing). Single TL071s are not
  mirrored, so their V+ pin goes up to the B+ rail.
- `verify_sch.py` treats R/C pins as interchangeable; "unconnected-*" nets are the unused TL071 offset/NC pins.
- KiCad 7's CLI has no ERC command. Run ERC in the GUI.

## Open items / assumptions
- R3, R5, R10, R11 = 4.7k (original: 3.3k–6.8k, matched to C2–C5). R4, R9 = 4.7k (original: "chosen to match
  select. pot"; 4.7k reproduces the manual's 40–50 Hz minimum bandwidth).
- C9/C10: value not on original (DNP). C7: not used in QF-1 (DNP). C2–C5 read as .018 µF.
- Screw terminals J101/J102: wire-entry side assumed; check in the 3D viewer.
- The amp board's Sallen-Key corner works out at about 1.45 kHz from the scanned values; worth measuring.
