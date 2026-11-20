"""QF-1 board hookup (wiring of boards, pots, switch, jacks)."""
from sch import S, FONTB, FONT


def draw_hookup(c, ox, oy, s):
    d = S(c, ox, oy, s)
    T = d.text

    # ---------------- Audio / AC supply board
    d.rect(200, 40, 700, 170, w=1.5)
    T(430, 98, "AUDIO/AC SUPPLY\nBOARD", 10, "l", FONTB)
    # RF ground screw
    d.ocircle(240, 100, 7, w=1.2)
    d.line((235, 105), (245, 95))
    d.wire((240, 107), (240, 170))
    d.arrow((150, 70), (232, 96), size=7)
    T(50, 48, "Direct RF ground\nto chassis\nthrough screw", 8.5, "l")
    # terminals
    d.dot(240, 170)
    T(246, 164, "GND", 8, "l")
    d.dot(560, 170)
    T(560, 164, "IN", 8, "c")
    d.dot(680, 170)
    T(680, 164, "B+", 8, "c")
    d.dot(680, 40)
    T(674, 34, "AUDIO OUT", 8, "r")

    # Audio out -> phone/speaker jack
    JX, JY = 800, 110
    d.wire((680, 40), (680, 22), (760, 22), (760, JY - 18), (JX, JY - 18), (JX, JY - 8))
    d.c.setLineWidth(1.2 * s)
    d.c.circle(d.X(JX), d.Y(JY), 8 * s, stroke=1, fill=0)
    d.line((JX - 5, JY - 2), (JX, JY + 4), (JX + 5, JY - 2))
    d.line((JX + 8, JY), (JX + 16, JY))
    T(JX + 20, JY + 3, "Phone/Spkr Out", 9, "l")
    # jack sleeve to chassis ground
    CGX, CGY = 800, 150
    d.wire((JX, JY + 8), (JX, CGY))
    d.dot(CGX, CGY)
    d.wire((CGX, CGY), (835, CGY))
    d.chassis(835, CGY, lead=6)
    T(850, CGY + 2, "Chassis Gnd.", 9, "l")
    T(850, CGY + 14, "Front Panel", 9, "l", "LSansI")

    # ---------------- Main board
    MX1, MY1, MX2, MY2 = 200, 270, 700, 420
    d.rect(MX1, MY1, MX2, MY2, w=1.5)
    T(430, 335, "MAIN BOARD", 10, "c", FONTB)
    top = {21: 300, 20: 430, 1: 680}
    for n, x in top.items():
        d.dot(x, MY1)
    T(300, MY1 + 14, "21", 8.5, "c")
    T(430, MY1 + 14, "20 (QF-1 GND)", 8.5, "l")
    T(680, MY1 + 14, "1", 8.5, "c")
    right = {14: 292, 17: 312, 19: 332, 3: 352, 11: 372, 10: 392}
    for n, y in right.items():
        d.dot(MX2, y)
        T(MX2 - 6, y + 3, str(n), 8.5, "r")
    bot = {5: 215, 6: 232, 8: 255, 18: 370, 13: 395, 16: 415, 9: 480, 15: 560, 12: 650}
    for n, x in bot.items():
        d.dot(x, MY2)
        T(x, MY2 - 6, str(n), 8.5, "c")
    d.dot(MX1, 320)
    T(MX1 + 6, 323, "4  INPUT", 8.5, "l")
    d.dot(MX1, 345)
    T(MX1 + 6, 348, "7  GND (QF-2)", 8.5, "l")

    # interconnections between boards
    # GND -> chassis ground node
    d.wire((240, 170), (240, 200), (CGX, 200), (CGX, CGY), hops=[(560, 200), (680, 200)][0:0])
    # IN -> 21
    d.wire((560, 170), (560, 232), (300, 232), (300, MY1), hops=[(560, 200)])
    # 20 -> chassis ground
    d.wire((430, MY1), (430, 246), (CGX, 246), (CGX, 200), hops=[(680, 246)])
    d.dot(CGX, 200)
    # B+ -> 1
    d.wire((680, 170), (680, MY1), hops=[(680, 200), (680, 246)])

    # ---------------- input plug, shielded cable, RF bypass
    # plug
    d.rect(95, 308, 128, 334, w=1.3)
    d.line((72, 316), (95, 316), w=1.3)
    d.line((72, 326), (95, 326), w=1.3)
    d.c.setLineWidth(1.3 * s)
    p = d.c.beginPath()
    p.arc(d.X(64), d.Y(331), d.X(76), d.Y(311), 90, 180)
    d.c.drawPath(p, stroke=1, fill=0)
    T(20, 318, "Input\nPlug", 9, "l")
    # inner conductor to pin 4
    d.wire((128, 320), (MX1, 320))
    d.dot(182, 320)
    # shield (braid drawn as loops) to rear panel ground
    d.line((128, 330), (172, 330), (172, 356), (150, 356))
    d.arrowhead(146, 356, 180, 6)
    T(118, 372, "To rear\npanel gnd.", 7.5, "l", "LSansI")
    for x in (138, 150, 162):
        d.c.setLineWidth(0.9 * s)
        d.c.ellipse(d.X(x - 3.5), d.Y(333), d.X(x + 3.5), d.Y(313), stroke=1, fill=0)
    # RF bypass .001 to rear panel gnd
    d.wire((182, 320), (182, 290))
    d.cap((182, 290), (146, 290))
    d.arrow((146, 290), (120, 290), size=5)
    T(116, 293, "To rear\npanel gnd.", 7.5, "r", "LSansI")
    T(164, 266, ".001\u00b5F\nRF Bypass", 7.5, "c", "LSansI")

    # ---------------- selectivity & frequency pots
    PT, PB = 448, 506   # pot top/bottom
    # 5 & 6 tied; 5 -> front selectivity wiper and -> switch 1 PK
    d.wire((215, MY2), (215, 432), (232, 432), (232, MY2))
    d.wire((215, 432), (215, 560), (720, 560), (720, 472), (775, 472), (775, 483),
           hops=[(740, 472)])
    d.dot(215, 432)
    # front selectivity pot (top = 8)
    d.wire((255, MY2), (255, 440))
    d.dot(255, 440)
    d.pot((255, 440), (255, PB), side=-1, wiper_len=40)
    d.dot(215, 473)
    # 8 also -> front frequency wiper
    d.wire((255, 440), (275, 440), (275, 540), (452, 540), (452, 481))
    # rear selectivity (top = 18)
    d.wire((370, MY2), (370, 436))
    d.dot(370, 436)
    d.pot((370, 436), (370, 504), side=1, wiper_len=25)
    d.wire((395, MY2), (395, 470))
    d.wire((415, MY2), (415, 470), (395, 470))
    d.dot(395, 470)
    # 18 -> rear frequency wiper (hop over 13, 16, 9, 15)
    d.wire((370, 436), (585, 436), (585, 481), hops=[(395, 436), (415, 436), (480, 436), (560, 436)])
    # frequency pots
    d.wire((480, MY2), (480, 452))
    w1 = d.pot((480, 452), (480, PB + 4), side=-1, wiper_len=28)
    d.wire((560, MY2), (560, 452))
    d.pot((560, 452), (560, PB + 4), side=1, wiper_len=25)
    # gang dashes
    d.line((243, 486), (243, 520), (385, 520), (385, 488), dash=(6, 3))
    d.line((468, 494), (468, 526), (575, 526), (575, 494), dash=(6, 3))
    # labels
    T(310, 584, "Front   Rear\nSelectivity\n(Dual pot)\n500K", 9, "c")
    T(520, 584, "Front   Rear\nFrequency\n(Dual pot)\n500K", 9, "c")

    # ---------------- function switch (2 poles)
    def pole(cx, cy):
        d.dot(cx, cy)
        for i, lab in enumerate(("PK", "NTCH", "LP")):
            y = cy - 18 + i * 18
            d.ocircle(cx + 38, y)
            T(cx + 44, y - 3, lab, 7.5, "l")
        d.line((cx, cy), (cx + 30, cy - 15), w=1.3)
        d.arrowhead(cx + 35.5, cy - 17, -27, 6)
    pole(740, 500)
    pole(860, 500)
    # 12 -> pole 1 common
    d.wire((650, MY2), (650, 452), (740, 452), (740, 500), hops=[(740, 472)][0:0])
    # 10 -> NTCH1, 11 -> LP1
    d.wire((MX2, 392), (800, 392), (800, 500), (781, 500))
    d.wire((MX2, 372), (815, 372), (815, 518), (781, 518))
    # 3 -> pole 2 common
    d.wire((MX2, 352), (845, 352), (845, 500), (860, 500))
    # 19 -> PK2, 17 -> NTCH2, 14 -> LP2
    d.wire((MX2, 332), (925, 332), (925, 482), (901, 482))
    d.wire((MX2, 312), (945, 312), (945, 500), (901, 500))
    d.wire((MX2, 292), (965, 292), (965, 518), (901, 518))
    d.line((740, 506), (740, 540), (860, 540), (860, 506), dash=(6, 3))
    # rotation notes
    d.arrow((1000, 470), (1000, 560), size=8)
    T(1010, 490, "Clockwise\nSwitch\nRotation", 9, "l")
    d.arrow((180, 470), (180, 560), size=8)
    T(30, 470, "Clockwise pot\nRotation\n(Bottom = left\npot terminal\nas viewed from\nfront)", 8.5, "l")
