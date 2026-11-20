"""Build a KiCad 7 PCB from the schematic's exported netlist + a placement table,
autoroute with Freerouting, add GND pours, run DRC."""
import json
import os
import subprocess
os.environ.setdefault("KICAD7_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
os.environ.setdefault("KICAD7_SYMBOL_DIR", "/usr/share/kicad/symbols")
import pcbnew
from sexp import parse, find, findall, Sym

FPDIR = "/usr/share/kicad/footprints/"
from paths import FR
OX, OY = 100.0, 100.0          # board origin (mm) in KiCad coordinates


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))


def read_netlist(path):
    e = parse(open(path).read())[0]
    comps = {}
    for c in findall(find(e, Sym("components")), Sym("comp")):
        ref = find(c, Sym("ref"))[1]
        ts = find(c, Sym("tstamps"))
        comps[ref] = dict(value=find(c, Sym("value"))[1], fp=find(c, Sym("footprint"))[1],
                          tstamp=str(ts[1]).split()[0] if ts else "")
    nets = {}
    for n in findall(find(e, Sym("nets")), Sym("net")):
        name = find(n, Sym("name"))[1].lstrip("/")
        nodes = [(find(nd, Sym("ref"))[1], find(nd, Sym("pin"))[1]) for nd in findall(n, Sym("node"))]
        nets[name] = nodes
    return comps, nets


PRO_TEMPLATE = {
    "board": {"design_settings": {
        "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.5,
                     "copper_text_size_v": 1.5, "copper_text_thickness": 0.3, "silk_line_width": 0.15,
                     "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
        "rules": {"min_clearance": 0.2, "min_track_width": 0.25, "min_via_diameter": 0.6,
                  "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.5,
                  "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25, "min_silk_clearance": 0.0},
        "track_widths": [0.0, 0.4, 0.8, 1.2], "via_dimensions": [{"diameter": 0.0, "drill": 0.0},
                                                                {"diameter": 1.0, "drill": 0.5}]}},
    "meta": {"filename": "", "version": 1},
    "net_settings": {
        "classes": [
            {"name": "Default", "clearance": 0.25, "track_width": 0.4, "via_diameter": 1.0, "via_drill": 0.5,
             "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "line_style": 0, "wire_width": 6, "bus_width": 12,
             "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"},
            {"name": "Power", "clearance": 0.3, "track_width": 0.8, "via_diameter": 1.2, "via_drill": 0.6,
             "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "line_style": 0, "wire_width": 6, "bus_width": 12,
             "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}],
        "meta": {"version": 3}, "net_colors": None, "netclass_assignments": None, "netclass_patterns": []},
    "pcbnew": {"page_layout_descr_file": ""},
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
    "sheets": [], "text_variables": {}, "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
}

EMPTY_PCB = """(kicad_pcb (version 20221018) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers
    (0 "F.Cu" signal) (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2") (44 "Edge.Cuts" user)
    (45 "Margin" user) (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user) (49 "F.Fab" user)
  )
  (setup (pad_to_mask_clearance 0)
    (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros false) (usegerberextensions false) (usegerberattributes true)
      (usegerberadvancedattributes true) (creategerberjobfile true) (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000) (svgprecision 4) (plotframeref false) (viasonmask false) (mode 1)
      (useauxorigin false) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15.000000) (dxfpolygonmode true)
      (dxfimperialunits true) (dxfusepcbnewfont true) (psnegative false) (psa4output false) (plotreference true)
      (plotvalue true) (plotinvisibletext false) (sketchpadsonfab false) (subtractmaskfromsilk false)
      (outputformat 1) (mirror false) (drillshape 0) (scaleselection 1) (outputdirectory "gerbers/"))
  )
  (net 0 "")
)
"""


def build(name, outdir, placement, size, power_nets, silk=(), holes_gnd=(), title="", rev="1.0",
          route=True, passes=40, ref_pos=None):
    W, H = size
    os.makedirs(outdir, exist_ok=True)
    pcb_path = f"{outdir}/{name}.kicad_pcb"
    pro_path = f"{outdir}/{name}.kicad_pro"
    pro = json.loads(json.dumps(PRO_TEMPLATE))
    pro["meta"]["filename"] = f"{name}.kicad_pro"
    pro["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": n} for n in power_nets]
    json.dump(pro, open(pro_path, "w"), indent=2)
    open(pcb_path, "w").write(EMPTY_PCB)
    board = pcbnew.LoadBoard(pcb_path)

    comps, nets = read_netlist(f"{outdir}/{name}.net")
    netobj = {}
    for nname in nets:
        ni = pcbnew.NETINFO_ITEM(board, nname)
        board.Add(ni)
        netobj[nname] = ni
    pin_net = {(r, p): n for n, nodes in nets.items() for (r, p) in nodes}

    missing = [r for r in comps if r not in placement]
    if missing:
        raise SystemExit(f"no placement for {missing}")
    for ref, c in comps.items():
        lib, fpn = c["fp"].split(":")
        fp = pcbnew.FootprintLoad(FPDIR + lib + ".pretty", fpn)
        fp.SetFPID(pcbnew.LIB_ID(lib, fpn))
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        x, y, rot = placement[ref][:3]
        side = placement[ref][3] if len(placement[ref]) > 3 else "F"
        fp.SetPosition(mm(x, y))
        fp.SetOrientationDegrees(rot)
        if c["tstamp"]:
            fp.SetPath(pcbnew.KIID_PATH("/" + c["tstamp"]))
        if ref.startswith("H"):
            fp.Reference().SetVisible(False)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        fp.Reference().SetTextThickness(pcbnew.FromMM(0.12))
        if ref_pos and ref in ref_pos:
            rx, ry = ref_pos[ref][:2]
            fp.Reference().SetPosition(mm(rx, ry))
            fp.Reference().SetTextAngle(pcbnew.EDA_ANGLE(ref_pos[ref][2] if len(ref_pos[ref]) > 2 else 0, pcbnew.DEGREES_T))
        board.Add(fp)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netobj[n])
        if ref.startswith("H") and ref in holes_gnd:
            for pad in fp.Pads():
                pad.SetNet(netobj["GND"])

    # outline with 3 mm corner radius
    r = 3.0
    edge = pcbnew.Edge_Cuts
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(mm(*a)); s.SetEnd(mm(*b)); s.SetLayer(edge); s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)
    def arc(c, start, ang):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(mm(*c)); s.SetStart(mm(*start)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
        s.SetLayer(edge); s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)
    seg((r, 0), (W - r, 0)); seg((W, r), (W, H - r)); seg((W - r, H), (r, H)); seg((0, H - r), (0, r))
    arc((W - r, r), (W - r, 0), 90); arc((W - r, H - r), (W, H - r), 90)
    arc((r, H - r), (r, H), 90); arc((r, r), (0, r), 90)

    for (txt, x, y, size, layer) in silk:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt)
        t.SetPosition(mm(x, y))
        t.SetLayer(pcbnew.F_SilkS if layer == "F" else pcbnew.B_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
        t.SetTextThickness(pcbnew.FromMM(max(0.15, size * 0.15)))
        if layer == "B":
            t.SetMirrored(True)
        board.Add(t)

    tb = board.GetTitleBlock()
    tb.SetTitle(title); tb.SetRevision(rev); tb.SetDate("2026-11-19")
    tb.SetCompany("Redrawn from Autek Research QF-1 manual")
    pcbnew.SaveBoard(pcb_path, board)
    return board, pcb_path


def autoroute(board, pcb_path, passes=40):
    dsn = pcb_path.replace(".kicad_pcb", ".dsn")
    ses = pcb_path.replace(".kicad_pcb", ".ses")
    pcbnew.ExportSpecctraDSN(board, dsn)
    r = subprocess.run(["xvfb-run", "-a", "java", "-jar", FR, "-de", dsn, "-do", ses,
                        "-mp", str(passes)], capture_output=True, text=True, timeout=1200)
    if not os.path.exists(ses):
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit("freerouting failed")
    import_ses(board, ses)
    return r


def import_ses(board, ses):
    """minimal Specctra session importer (wires + vias) for scripted use"""
    import re
    e = parse(open(ses).read())[0]
    routes = find(e, Sym("routes"))
    res = find(routes, Sym("resolution"))
    unit = {"um": 1e-3, "mm": 1.0, "mil": 0.0254, "inch": 25.4}[str(res[1])] / float(res[2])
    C = lambda v: pcbnew.FromMM(float(v) * unit)
    for k in list(board.Tracks()):
        board.Remove(k)
    lay = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    n_w = n_v = 0
    for net in findall(find(routes, Sym("network_out")), Sym("net")):
        ni = board.FindNet(str(net[1]))
        for w in findall(net, Sym("wire")):
            p = find(w, Sym("path"))
            layer, width = lay[str(p[1])], C(p[2])
            pts = [(C(p[i]), -C(p[i + 1])) for i in range(3, len(p) - 1, 2)]
            for a, b in zip(pts[:-1], pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(*a)); t.SetEnd(pcbnew.VECTOR2I(*b))
                t.SetWidth(width); t.SetLayer(layer); t.SetNet(ni)
                board.Add(t); n_w += 1
        for v in findall(net, Sym("via")):
            m = re.search(r"_(\d+):(\d+)_um", str(v[1]))
            dia, drill = (int(m.group(1)), int(m.group(2))) if m else (1000, 500)
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(C(v[2]), -C(v[3])))
            via.SetWidth(pcbnew.FromMM(dia / 1000)); via.SetDrill(pcbnew.FromMM(drill / 1000))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(ni)
            board.Add(via); n_v += 1
    print(f"imported {n_w} track segments, {n_v} vias")


def add_pours(board, W, H, net="GND"):
    gnd = board.FindNet(net)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetIsRuleArea(False)
        z.SetLocalClearance(pcbnew.FromMM(0.4))
        z.SetMinThickness(pcbnew.FromMM(0.3))
        z.SetThermalReliefGap(pcbnew.FromMM(0.4))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for (x, y) in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
            ol.Append(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def drc(board, pcb_path):
    rpt = pcb_path.replace(".kicad_pcb", "-drc.rpt")
    pcbnew.WriteDRCReport(board, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt
