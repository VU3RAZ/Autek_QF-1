# Autek QF-1 Audio Filter: KiCad 7 projects

Two KiCad 7 projects recreated from the original Autek QF-1 manual schematics.
Each has a wired schematic laid out like the original drawing and a routed 2-layer through-hole PCB.

| Folder | Board | Size |
|---|---|---|
| `QF1_Main_Filter/` | Main filter board: two cascaded state-variable sections (U1 to U3) and output amp U4 | 114 x 84 mm |
| `QF1_Amp_Supply/` | Audio power amp (Sallen-Key + BC337/BC327 follower) and DC supply | 92 x 64 mm |

Each folder contains:
- `*.kicad_pro`, `*.kicad_sch`, `*.kicad_pcb`: open the `.kicad_pro` in KiCad 7 or later.
- `QF1.kicad_sym` and `sym-lib-table`: the project-local `B+` power symbol.
- `fab/*-gerbers.zip`: Gerbers (both copper layers, mask, silkscreen, outline), Excellon drill file and job file, ready to upload to a PCB fab.
- `docs/`: schematic PDF, top/bottom copper PDFs, assembly drawing, BOM (CSV) and DRC report.

## Checks performed
- Schematic connectivity: the netlist KiCad exports from each schematic was compared net by net against the circuit traced from the original manual. Both match exactly.
- PCB: every pad's net matches the original circuit. Freerouting routed 100% (0 unconnected pads, no vias needed). DRC shows **0 errors**; only cosmetic silkscreen-overlap warnings remain.
- KiCad 7's command-line tool has no ERC command. Run *Inspect > Electrical Rules Checker* once in your KiCad. Expect at most "dangling wire end" notes where the original drawing's rails end.

## Changes from the 1970s original
- **U1, U2, U3: TL072** (dual, 8-pin) replace the µA747 (dual, 14-pin). The A/B halves keep the original U1A to U3B roles and pin labels on the schematic. U4 and U101 are **TL071** in place of the µA741 (same pinout).
- **Q101/Q102: BC337/BC327** replace MPS6560/MPS6562, using the wide-pitch TO-92 footprint (CBE order, as on the original layout).
- **Supply:** the mains transformer, ON-OFF switch and line caps C107/C108 are **off-board**. J101 takes 12 to 15 VAC from the transformer secondary (outer ends of the original centre-tapped winding; CT unused) or from an AC wall adapter. A 4-diode bridge (D102 to D105) replaces the original 2-diode centre-tap rectifier. C106 is uprated to 35 V.
- **Added:** C13 (47 µF), C14 and C15 (100 nF) supply decoupling on the main board, and C109 (100 nF) on the amp board.
- **Mounting:** H101 is a plated M3 hole on GND, the original "direct RF ground to chassis through screw". The other holes are unplated.

## Values to confirm on test (as the original notes say)
- R3, R5, R10, R11: fitted as 4.7K. The original says 3.3K to 6.8K, chosen to match C2 to C5 (C2 to C5 matched to 1 %).
- R4, R9: fitted as 4.7K. The original says "chosen to match select. pot" and gives no value; 4.7K is an estimate from the circuit, so adjust for the selectivity range you want.
- C9, C10: no value on the original (in parallel with R17/R14). Footprints are provided and marked DNP.
- C7: "not included in QF-1" (QF-2 output). Marked DNP.
- C2 to C5 are read as .018 µF (C3 is partly illegible on the scan).

## Panel wiring (unchanged; board pin numbers are on the silkscreen)
J1 = board pins 1 to 7, J2 = board pins 8 to 19, J3 = pin 20 (GND), J4 = pin 21 (QF-1 out).
- 5 and 6 tied to the front SELECTIVITY wiper; 8 to the top of front SELECTIVITY and to the front FREQUENCY wiper; 9 to the top of front FREQUENCY.
- 13 and 16 tied to the rear SELECTIVITY wiper; 18 to the top of rear SELECTIVITY and to the rear FREQUENCY wiper; 15 to the top of rear FREQUENCY.
- Pots are dual 500K (front/rear sections); bottom terminals are left open. Clockwise rotation selects lower frequency.
- Function switch pole 1: common 12, PK 5, NTCH 10, LP 11. Pole 2: common 3, PK 19, NTCH 17, LP 14.
- Main board 21 goes to amp board IN; 20 and the amp board GND go to chassis; amp board B+ goes to main board 1.

## Please check before ordering boards
- **Screw terminal orientation:** J101/J102 are placed with the wire entry assumed on the deeper side of the KiCad footprint, so they face the board edges. Confirm in the 3D viewer.
- The routing is autorouted (Freerouting) and DRC-clean. Give it a visual once-over in KiCad and tidy any track you'd like shorter.
