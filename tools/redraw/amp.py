"""QF-1 Audio power amp / AC supply board schematic + layout."""
from sch import S, FONTB


def draw_amp(c, ox, oy, s):
    d = S(c, ox, oy, s)
    T = d.text
    # chassis boundary (dashed, not a conductor)
    BX1, BY1, BX2, BY2 = 20, 20, 640, 360
    d.rect(BX1, BY1, BX2, BY2, w=1.0, dash=(7, 4))

    GB = 305  # ground bus y
    BP = 60   # B+ rail y

    # --- input & Sallen-Key low pass around U101
    d.term(BX1, 152)
    T(BX1 - 6, 156, "In", 9, "r", FONTB)
    d.res((BX1, 152), (100, 152))
    T(60, 170, "R101\n12K", 7.5, "c")
    d.dot(100, 152)
    d.res((100, 152), (172, 152))
    T(136, 170, "R102\n100K", 7.5, "c")
    d.dot(172, 152)
    u = d.opamp(190, 140, "U101\n", pins=dict(inv=2, non=3, out=6, top=7, bot=4))
    T(216, 150, "µA741", 7, "c")
    d.wire((172, 152), u["non"])
    # C101 from R101/R102 junction to (-) input
    d.wire((100, 152), (100, 128))
    d.cap((100, 128), (172, 128))
    T(136, 112, "C101\n.01", 7.5, "c")
    d.dot(172, 128)
    d.wire((172, 128), u["inv"])
    # C102 from (+) to ground
    d.cap((172, 152), (172, 230))
    T(160, 186, "C102\n.001", 7.5, "r")
    d.wire((172, 230), (172, GB))
    # pin 4 to ground
    d.wire(u["bot"], (u["bot"][0], GB))
    # pin 7 to B+ rail, hopping over the C103 line
    px = u["top"][0]
    d.wire(u["top"], (px, BP), hops=[(px, 95)])
    # C103: from (-) node to driver node
    d.wire((172, 128), (172, 95))
    d.dot(172, 95)
    d.wire((172, 95), (215, 95))
    d.cap((215, 95), (300, 95))
    T(257, 80, "C103\n.001", 7.5, "c")
    d.wire((300, 95), (310, 95), (310, 140))
    # feedback from emitter node to (-) input
    d.wire((172, 95), (172, 45), (380, 45))
    # output -> R103 -> driver node
    d.res(u["out"], (310, 140))
    T(276, 124, "R103\n100", 7.5, "c")
    d.dot(310, 140)

    # bias chain R104 / D101 / R105
    d.res((310, 140), (310, 182))
    T(302, 166, "R104\n39", 7.5, "r")
    d.diode((310, 182), (310, 220))
    T(302, 198, "D101\n(1N4001)", 7.5, "r")
    d.dot(310, 220)
    d.res((310, 220), (310, GB))
    T(302, 262, "R105\n1K", 7.5, "r")

    # Q101 (NPN, collector up) and Q102 (PNP, emitter up)
    d.wire((310, 140), (345, 140))
    c1, e1 = d.bjt(345, 140, "npn", c_up=True)
    T(338, 134, "B", 7, "r")
    T(363, 120, "C", 7, "l")
    T(363, 165, "E", 7, "l")
    T(386, 128, "Q101\nMPS6560", 7.5, "l")
    d.wire((310, 220), (345, 220))
    c2, e2 = d.bjt(345, 220, "pnp", c_up=False)
    T(338, 214, "B", 7, "r")
    T(363, 203, "E", 7, "l")
    T(363, 246, "C", 7, "l")
    T(386, 232, "Q102\nMPS6562", 7.5, "l")
    # collectors
    d.res(c1, (c1[0], BP))
    T(368, 86, "R106\n3.3Ω", 7.5, "l")
    d.res(c2, (c2[0], GB))
    T(368, 276, "R107\n3.3Ω", 7.5, "l")
    # emitter node
    d.wire(e1, (e1[0], 185))
    d.wire(e2, (e2[0], 185))
    d.dot(359, 185)
    T(386, 209, "(7.5V NO LOAD)", 6.5, "l")
    d.wire((359, 185), (380, 185))
    d.dot(380, 185)
    d.wire((380, 185), (380, 45), hops=[(380, BP)])

    # C104 output coupling
    d.cap((380, 185), (430, 185), polar="p1")
    T(405, 166, "C104\n100µF", 7.5, "c")
    d.dot(430, 185)
    # audio out terminal (top boundary)
    d.wire((430, 185), (430, BY1), hops=[(430, BP)])
    d.term(430, BY1)
    T(430, 12, "Audio Out", 8.5, "c", FONTB)
    # R108 and C105 to ground
    d.res((430, 185), (430, GB))
    T(437, 250, "R108\n390", 7.5, "l")
    d.wire((430, 185), (465, 185))
    d.cap((465, 185), (465, GB))
    T(474, 232, "C105\n.1–.22\n(RF\nBYPASS)", 7, "l")

    # B+ rail
    d.wire((px, BP), (640 - 5, BP))
    for x in (359,):
        d.dot(x, BP)
    d.dot(540, BP)
    d.wire((540, BP), (540, BY1))
    d.term(540, BY1)
    T(540, 12, "B+", 8.5, "c", FONTB)

    # C106 filter cap
    d.cap((540, BP), (540, 130), polar="p1")
    T(548, 88, "C106\n1000µF\n25V", 7.5, "l")
    T(500, 92, "B+\n(15V no\nload)", 7.5, "r")
    d.dot(540, 130)

    # transformer
    d.coil_h(560, 620, 196, n=6, up=True)    # secondary (top)
    d.coil_h(560, 620, 212, n=6, up=False)   # primary
    d.line((558, 202), (622, 202), w=1.4)
    d.line((558, 206), (622, 206), w=1.4)
    T(552, 192, "3", 8, "r", FONTB)
    T(628, 192, "4", 8, "l", FONTB)
    T(552, 222, "2", 8, "r", FONTB)
    T(628, 222, "1", 8, "l", FONTB)
    T(590, 240, "XFRMR", 8.5, "c", FONTB)
    # rectifier: D102 / D103 anodes joined (to ground), cathodes to winding ends
    d.wire((560, 196), (560, 150))
    d.wire((620, 196), (620, 150))
    d.diode((590, 150), (560, 150))
    d.diode((590, 150), (620, 150))
    d.dot(590, 150)
    T(574, 142, "D102", 7, "c")
    T(607, 142, "D103", 7, "c")
    # anodes -> ground line
    d.wire((590, 150), (590, 130), (505, 130), (505, GB))
    # CT -> B+
    d.wire((590, 190), (590, 172), (632, 172), (632, BP), hops=[(620, 172)])
    T(594, 182, "CT", 6.5, "l")

    # primary, switch, line caps, plug
    d.wire((620, 212), (620, 226), (BX2, 226))
    d.term(BX2, 226)
    d.term(BX2, 262)
    d.wire((BX2, 226), (660, 226))
    d.switch_spst(660, 230, 258)
    d.wire((660, 262), (BX2, 262))
    T(672, 246, "ON-\nOFF", 7.5, "l")
    d.wire((BX2, 262), (620, 262), (620, 280))
    d.wire((560, 212), (560, 280))
    d.dot(560, 280)
    d.dot(620, 280)
    d.cap((560, 280), (590, 280))
    d.cap((590, 280), (620, 280))
    d.dot(590, 280)
    T(575, 302, "C107\n.01 1KV", 5.8, "c")
    T(605, 302, "C108\n.01 1KV", 5.8, "c")
    # line caps midpoint to ground
    d.wire((590, 280), (590, 292), (505, 292), hops=[(560, 292)])
    d.dot(505, 292)
    d.wire((560, 280), (560, BY2), hops=[(560, GB)] if False else [])
    d.wire((620, 280), (620, BY2))
    d.term(560, BY2)
    d.term(620, BY2)
    d.wire((560, BY2), (560, 384))
    d.wire((620, BY2), (620, 384))
    # plug body
    d.line((548, 384), (632, 384), w=1.4)
    d.c.setLineWidth(1.3 * s)
    p = c.beginPath()
    p.arc(d.X(548), d.Y(402), d.X(632), d.Y(370), 180, 180)
    c.drawPath(p, stroke=1, fill=0)
    T(645, 395, "115 VAC\nPLUG", 7.5, "l")

    # ground bus
    d.wire((172, GB), (505, GB))
    for x in (215, 310, 359, 430, 465):
        d.dot(x, GB)
    d.dot(u["bot"][0], GB)
    d.wire((80, GB), (172, GB))
    d.dot(172, GB)
    d.dot(130, GB)
    d.wire((130, GB), (130, BY2))
    d.term(130, BY2)
    T(130, 376, "Gnd", 8.5, "c", FONTB)
    d.dot(80, GB)
    d.chassis(80, GB, lead=14)
    T(92, 296, "GND TO CHASSIS", 7, "l")
    d.dot(505, GB)


def draw_amp_layout(c, ox, oy, s):
    """Component-side layout of the power amp / AC supply board."""
    d = S(c, ox, oy, s, lw=1.0)
    T = d.text
    d.rect(0, 30, 300, 130, w=1.3)
    # top holes
    for x in (20, 34, 74, 88):
        d.ocircle(x, 42, 2.4)
    d.line((20, 39), (16, 18))
    d.line((34, 39), (30, 18))
    d.line((74, 39), (70, 18))
    d.line((88, 39), (84, 18))
    T(23, 12, "115 VAC", 7, "c")
    T(80, 4, "On-off\nSwitch", 7, "c")
    # U101
    d.rect(145, 48, 172, 64)
    T(158.5, 59.5, "U101", 6.5, "c")
    d.arrow((166, 42), (150, 42), size=3.5, w=0.7)
    T(147, 44, "4", 5.5, "r")
    T(170, 44, "1", 5.5, "l")
    d.arrow((152, 72), (166, 72), size=3.5, w=0.7)
    T(149, 74, "5", 5.5, "r")
    T(169, 74, "8", 5.5, "l")
    # audio out
    d.ocircle(210, 42, 2.4)
    d.line((210, 39), (210, 24))
    T(210, 12, "Audio\nOut", 7, "c")
    # transistors (TO-92 flats)
    c.setLineWidth(1.0 * s)
    p = c.beginPath()
    p.arc(d.X(200), d.Y(62), d.X(222), d.Y(46), 180, 180)
    c.drawPath(p, stroke=1, fill=0)
    d.line((200, 54), (222, 54))
    T(196, 66, "C B E", 5.5, "l")
    p = c.beginPath()
    p.arc(d.X(222), d.Y(78), d.X(238), d.Y(60), -90, 180)
    c.drawPath(p, stroke=1, fill=0)
    d.line((230, 60), (230, 78))
    T(226, 66, "E\nB\nC", 4.8, "c")
    d.arrow((262, 46), (218, 52), size=4, w=0.7)
    T(265, 49, "Q102", 7.5, "l")
    d.arrow((262, 66), (236, 68), size=4, w=0.7)
    T(265, 69, "Q101", 7.5, "l")
    # transformer: round core + mounting strap
    c.circle(d.X(90), d.Y(86), 30 * s, stroke=1, fill=0)
    d.line((22, 74), (160, 74))
    d.line((22, 98), (160, 98))
    p = c.beginPath()
    p.arc(d.X(10), d.Y(98), d.X(34), d.Y(74), 90, 180)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath()
    p.arc(d.X(148), d.Y(98), d.X(172), d.Y(74), -90, 180)
    c.drawPath(p, stroke=1, fill=0)
    d.ocircle(24, 86, 4)
    d.ocircle(158, 86, 4)
    d.line((60, 76), (60, 96), dash=(2, 2))
    d.line((120, 76), (120, 96), dash=(2, 2))
    # bottom holes
    for x, lab in ((20, "Gnd"), (175, "In"), (270, "B+")):
        d.ocircle(x, 118, 2.4)
        d.line((x, 121), (x, 140))
        T(x, 152, lab, 7.5, "c")
