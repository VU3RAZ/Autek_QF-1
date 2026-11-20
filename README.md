# Autek QF-1 Audio Filter: redraw, KiCad rebuild and analysis

A modern rework of the 1970s **Autek Research QF-1** tunable audio filter (peak / notch / low-pass, 250 Hz–2.5 kHz), made from the original 3-page manual.

| What | Where |
|---|---|
| Redrawn manual: full text plus vector schematics, hookup diagram and response curves | [`docs/Autek_QF-1_Instructions_Redrawn.pdf`](docs/Autek_QF-1_Instructions_Redrawn.pdf) |
| How the circuit works, stage by stage, with a performance rating | [`docs/QF1_How_It_Works.md`](docs/QF1_How_It_Works.md) |
| KiCad 7 projects: wired schematics plus routed 2-layer through-hole PCBs | [`kicad/`](kicad/) (see [`kicad/README.md`](kicad/README.md)) |
| Preview of both boards (schematics, copper, assembly) | [`docs/QF1_KiCad_Overview.pdf`](docs/QF1_KiCad_Overview.pdf) |
| Gerbers and drill files, ready for a PCB fab | `kicad/*/fab/*-gerbers.zip` |
| BOMs | `kicad/*/docs/*-BOM.csv` |
| Python generators (PDF redraw, schematics, PCB placement and routing) | [`tools/`](tools/) |

Original manual scan: <https://vtda.org/docs/radio/Autek/Autek_QF-1.pdf>

## Boards

- **QF1_Main_Filter** (114 × 84 mm): two cascaded state-variable filter sections (TL072 × 3, replacing the µA747) and the U4 output amp (TL071, replacing the µA741). Board pins 1–21 keep the original numbering for front-panel wiring.
- **QF1_Amp_Supply** (92 × 64 mm): a Sallen-Key low-pass driver, a BC337/BC327 push-pull output, and a bridge-rectified supply fed from 12–15 VAC off-board.

Both boards are fully routed. DRC shows 0 errors. Netlist and pad connectivity are verified against the original circuit.

## Before ordering boards

See [`kicad/README.md`](kicad/README.md). In particular: the values chosen on test (R3/R5/R10/R11, R4/R9), C9/C10 left unfitted (DNP), the screw-terminal wire-entry orientation, and running ERC once in KiCad.
