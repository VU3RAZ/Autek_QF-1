"""Wired KiCad schematic of the audio power amp / supply board, after the
original drawing; supply section changed to a bridge fed from off-board AC."""
from kisch import Sheet
from kib import KB
from design import AMP
from gen_sch import group
from paths import KOUT


def build_amp_wired():
    A = AMP["parts"]
    sh = Sheet(AMP["name"], AMP["title"], paper="A3", comments=(
        "U101 TL071 replaces uA741; Q101/Q102 BC337/BC327 replace MPS6560/MPS6562",
        "Mains transformer, ON-OFF switch and line caps C107/C108 are off-board",
        "Bridge D102-D105 accepts 12-15 VAC (original: centre-tapped secondary, 2 diodes)",
        "Dashed box = chassis boundary. H101 pad = direct RF ground to chassis screw"))
    kb = KB(sh, A, ox=30.0, oy=40.0, kx=1.75)
    kb.BX1, kb.BY1, kb.BX2, kb.BY2 = 20, 20, 700, 360
    d, L = kb, (lambda r: kb.text(0, 0, r))
    GB, BP = 305, 60
    d.rect(20, 20, 700, 360)
    # input network, Sallen-Key low-pass
    d.attach_net("IN", 20, 152)
    d.res((20, 152), (100, 152)); L("R101")
    d.dot(100, 152)
    d.res((100, 152), (172, 152)); L("R102")
    d.dot(172, 152)
    u = d.opamp(190, 140, "U101", mirror_single=True)
    d.wire((172, 152), u["non"])
    d.wire((100, 152), (100, 128))
    d.cap((100, 128), (172, 128)); L("C101")
    d.dot(172, 128)
    d.wire((172, 128), u["inv"])
    d.cap((172, 152), (172, 240)); L("C102")
    d.wire((172, 240), (172, GB))
    # C103 and overall feedback from the emitter node
    d.wire((172, 128), (172, 75))
    d.dot(172, 75)
    d.wire((172, 75), (215, 75))
    d.cap((215, 75), (300, 75)); L("C103")
    d.wire((300, 75), (310, 75), (310, 140))
    d.wire((172, 75), (172, 40), (410, 40), (410, 185))
    # driver, bias chain
    d.res(u["out"], (310, 140)); L("R103")
    d.dot(310, 140)
    d.res((310, 140), (310, 182)); L("R104")
    d.diode((310, 182), (310, 220)); L("D101")
    d.dot(310, 220)
    d.res((310, 220), (310, GB)); L("R105")
    # output transistors
    d.wire((310, 140), (345, 140))
    d._next_q = "Q101"
    c1, e1 = d.bjt(345, 140, "npn", c_up=True)
    d.wire((310, 220), (345, 220))
    d._next_q = "Q102"
    c2, e2 = d.bjt(345, 220, "pnp", c_up=False)
    EX = e1[0]
    d.res(c1, (c1[0], BP)); L("R106")
    d.res(c2, (c2[0], GB)); L("R107")
    d.wire(e1, (EX, 185))
    d.wire(e2, (EX, 185))
    d.dot(EX, 185)
    d.wire((EX, 185), (410, 185))
    d.dot(410, 185)
    # output coupling, load, RF bypass
    d.cap((410, 185), (460, 185), polar="p1"); L("C104")
    d.dot(460, 185)
    d.wire((460, 185), (460, 20))
    d.attach_net("AUDIO_OUT", 460, 20)
    d.res((460, 185), (460, GB)); L("R108")
    d.wire((460, 185), (495, 185))
    d.cap((495, 185), (495, GB)); L("C105")
    # B+ rail, reservoir, bridge
    d.wire((c1[0], BP), (650, BP))
    d.dot(c1[0], BP) if False else None
    d.wire((550, BP), (550, 20))
    d.attach_net("B+", 550, 20)
    d.cap((550, BP), (550, GB), polar="p1"); L("C106")
    d.cap((520, BP), (520, GB)); L("C109")
    for x in (520, 550, 600):
        d.dot(x, BP)
    d.diode((600, 185), (600, 100)); L("D102")
    d.wire((600, 100), (600, BP))
    d.diode((600, 280), (600, 185)); L("D104")
    d.wire((600, 280), (600, GB))
    d.diode((650, 185), (650, 100)); L("D103")
    d.wire((650, 100), (650, BP))
    d.diode((650, 280), (650, 185)); L("D105")
    d.wire((650, 280), (650, GB))
    d.dot(600, 185)
    d.dot(650, 185)
    d.wire((600, 185), (580, 185))
    X, Y = kb.P(580, 185); sh.label("AC1", X, Y, 180)
    d.wire((650, 185), (675, 185))
    X, Y = kb.P(675, 185); sh.label("AC2", X, Y, 0)
    # ground bus, chassis gnd, Gnd terminal
    d.wire((130, GB), (650, GB))
    for x in (172, 310, c2[0], 460, 495, 520, 550, 600):
        d.dot(x, GB)
    d.dot(130, GB) if False else None
    d.wire((130, GB), (130, 360))
    d.attach_net("GND", 130, 360)
    d.dot(250, GB)
    d.wire((250, GB), (250, 318))
    d.gnd(250, 318)
    kb.finish()
    for net, pt in {"NA": (100, 152), "NP": (172, 152), "EMIT": (410, 185), "OA_OUT": u["out"],
                    "DRV": (310, 140), "BIAS1": (310, 182), "BIAS2": (310, 220), "QC1": c1, "QC2": c2}.items():
        X, Y = kb.P(*pt)
        sh.label(net, X, Y, 0)
    sh.text("QF-1 FILTER — AUDIO PWR AMP / AC SUPPLY BOARD (wired from the original schematic)",
            30, 30, 2.5, bold=True)
    group(sh, A, "Board connections, AC input, chassis ground", 30, 135, 200,
          ["J101", "J102", "H101", "H102", "H103", "H104"])
    sh.pwr_flag("B+", 205.74, 140.97)
    sh.pwr_flag("GND", 213.36, 140.97)
    sh.text("AC IN: 12-15 VAC from the original transformer secondary (ends 3-4, CT unused)\n"
            "or an AC wall adapter. Keep mains wiring, fuse and ON-OFF switch off this board.\n"
            "Q101 ~7.5 V at the emitters with no load; B+ ~15-18 V no load.", 240, 150, 1.6)
    return sh


if __name__ == "__main__":
    sh = build_amp_wired()
    d = f"{KOUT}/{AMP['name']}"
    sh.save(f"{d}/{AMP['name']}.kicad_sch")
    print("ok")
