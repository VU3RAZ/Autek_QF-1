from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Flowable, NextPageTemplate, PageBreak,
                                KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import fonts
fonts.register()
from sch import S
from amp import draw_amp, draw_amp_layout
from hookup import draw_hookup
from mainboard import draw_main, draw_main_layout
from curves import draw_curves

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "Autek_QF-1_Instructions_Redrawn.pdf")
INK = colors.HexColor("#111111")

body = ParagraphStyle("body", fontName="LSerif", fontSize=10.5, leading=13.6,
                      alignment=TA_JUSTIFY, spaceAfter=6, textColor=INK)
h1 = ParagraphStyle("h1", fontName="LSansB", fontSize=34, leading=38, alignment=TA_CENTER,
                    spaceAfter=0, textColor=INK)
sub = ParagraphStyle("sub", fontName="LSansB", fontSize=10.5, leading=13, alignment=TA_CENTER,
                     spaceAfter=18, textColor=INK)
h2 = ParagraphStyle("h2", fontName="LSansB", fontSize=11.5, leading=14, spaceBefore=10,
                    spaceAfter=5, textColor=INK)
item = ParagraphStyle("item", parent=body, leftIndent=14)
cell = ParagraphStyle("cell", fontName="LSerif", fontSize=9.8, leading=12.2, textColor=INK)
cellh = ParagraphStyle("cellh", fontName="LSansB", fontSize=9.5, leading=12, alignment=TA_CENTER)
small = ParagraphStyle("small", fontName="LSerifI", fontSize=8.8, leading=11.2, spaceAfter=3,
                       textColor=colors.HexColor("#333333"))
cap = ParagraphStyle("cap", fontName="LSans", fontSize=8.8, leading=11.4, textColor=INK)


def P(t, st=body):
    return Paragraph(t, st)


class Drawing(Flowable):
    def __init__(self, fn, height, width=None):
        super().__init__()
        self.fn, self.h, self.w = fn, height, width

    def wrap(self, aw, ah):
        self.aw = aw
        return (self.w or aw, self.h)

    def draw(self):
        self.fn(self.canv, self.w or self.aw, self.h)


def title_block(c, x, y, w, h, lines):
    S(c, 0, 0, 1.0).c  # ensure ink
    c.setLineWidth(2.2)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFont("LSansB", 10)
    yy = y + h - 17
    for i, ln in enumerate(lines):
        c.setFont("LSansB", 10.5 if i == 0 else 9.5)
        c.drawString(x + 12 + i * 14, yy, ln)
        yy -= 14


def footer(c, doc):
    c.saveState()
    pw, ph = c._pagesize
    c.setFont("LSans", 7.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(36, 20, "Autek QF Series Audio Filters — Instructions (redrawn edition)")
    c.drawRightString(pw - 36, 20, f"Page {doc.page}")
    c.restoreState()


# ------------------------------------------------------------------ pages
def page_hookup(c, w, h):
    draw_hookup(c, 14, h - 6, 0.705)
    c.setFont("LSans", 8.8)
    txt = ["QF-1 Board Hookup. Note: Wiring to selectivity pot, frequency pot, and switch is identical for QF-2.",
           "For QF-2 input, output, ground, and B+, see figs. 1 to 3. For both models, see Main Board Layout",
           "drawing to identify physical position of numbered connections."]
    for i, t in enumerate(txt):
        c.drawString(230, 34 - i * 11.5, t)


def page_amp(c, w, h):
    draw_amp(c, 30, h - 4, 0.83)
    draw_amp_layout(c, 70, 182, 0.95)
    title_block(c, 430, 40, 290, 70, ["QF-1 FILTER", "AUDIO PWR AMP/AC SUPPLY  BOARD"])
    c.setFont("LSansI", 8)
    c.drawString(430, 24, "Dashed outline = chassis boundary; dots on it are leads leaving the board/chassis.")


def page_main(c, w, h):
    draw_main(c, 26, h + 2, 0.655)
    draw_main_layout(c, 60, 186, 0.78)
    # notes
    x, y = 405, 178
    c.setFont("LSansB", 9)
    c.drawString(x, y, "NOTES:")
    notes = ["0) R4 & R9 are chosen to match select. pot.",
             "1) R3, R5, R10 & R11 chosen to match C2, C3, C4 & C5.",
             "     Typical value is 3.3K to 6.8K.",
             "2) C2, C3, C4 & C5 matched to 1%.",
             "3) U1, U2 & U3 = µA747 ;  U4 = µA741"]
    c.setFont("LSans", 9)
    for i, n in enumerate(notes):
        c.drawString(x + 48, y - i * 12.5, n)
    title_block(c, 405, 18, 320, 76, ["QF FILTER", "MAIN BOARD", "SCHEMATIC / LAYOUT DRAWING"])


def page_curves(c, w, h):
    draw_curves(c, (w - 500) / 2, h - 10, 1.0)


# ------------------------------------------------------------------ text
story = []
story += [P("INSTRUCTIONS", h1), P("QF SERIES AUDIO FILTERS", sub)]
story += [P("Your audio filter was fully tested before shipment. Please study the instructions below to "
            "obtain best results. If you require parts not supplied, please obtain these at a local radio "
            "store since we do not stock them.")]

story += [P("A. INITIAL HOOKUP", h2)]
story += [P("<u>Model QF-1</u>. Plug the QF-1 into your receivers phone jack. Obtain an adaptor if size not "
            "compatible. Connect any impedance speaker or any high-impedance phone to output jack. To avoid "
            "hum or distortion with low-impedance phones, which are overly sensitive, use a series resistor. "
            "(See D. In Case of Trouble.) The QF-1 input may also be connected to the receiver speaker "
            "terminals. Be sure that the the cable shield (connected to the QF-1 chassis) is connected to the "
            "grounded speaker terminal. Otherwise, hum may be picked up.")]
story += [P("Note: This is rare, but a few types of CB radios and some Barlow Wadley radios require a "
            "resistor across their speaker or phone output; otherwise their audio outputs are not biased "
            "properly when connected to the QF-1 input. Try a resistor in the range of 10 to 100Ω.")]
story += [P("Connecting the QF-1 <u>output</u> to a <u>source</u> of voltage (e.g. a radios speaker output or "
            "power supply) can quickly burn out the filter, not covered by the warranty. (In-out switches, if "
            "added, may do this.) Never connect anything but a passive load (spkr., phones, another amps. "
            "<u>input</u>) to the filter <u>output</u>. Note: The filter <u>input</u> is protected by a 1000 "
            "volt capacitor and may be connected to virtually any source.")]

story += [P("B. FAMILIARIZATION", h2)]
story += [P("An audio filter has an effect roughly analogous to a tone control on a Hi-Fi set, i.e. it filters "
            "signals you tune in on your receiver and selects or rejects frequencies you desire. Of course "
            "your filters response is much sharper and more flexible than a simple tone control to cope with "
            "Shortwave signals. There are three adjustments:")]
story += [P("<b>1. Function Select Switch.</b> This switch selects (left to right) a peak, notch, or lowpass "
            "response. The peak (bandpass) function passes a narrow band of frequencies, while the notch "
            "function rejects a narrow band of frequencies. The peak or notch frequency is set by turning the "
            "frequency control. The lowpass function rejects high-frequency signals above the frequency set "
            "on the frequency control.", item)]
story += [P("<b>2. Selectivity Control (Pot).</b> This control adjusts the width of the notch and bandpass "
            "response, and also affects the lowpass rolloff and notch depth. Bandwidths from as small as "
            "40-50 HZ to essentially flat are available. The notch and peak widths are smallest with full "
            "rotation, but the notch depth decreases with more rotation (full clockwise = max. rotation). "
            "This control should not normally be rotated more than <b>60%</b> except in “peak.” "
            "Full rotation decreases notch depth and may lead to ringing in “lowpass.”", item)]
story += [P("<b>3. Frequency Control (Pot).</b> This control moves the peak, notch, and lowpass frequencies "
            "from approx. 250 Hz to 2500 Hz. This spans the entire range of useful communications "
            "frequencies. “Clockwise” rotation selects lower frequencies.", item)]
story += [P("Note: Volume coming out of the filter is adjusted with your receivers audio control. Note that "
            "the filter retains its full selectivity regardless of source, load, or slight overdrive, i.e. "
            "no “impedance matching” is required.")]

story += [P("C. USEFUL ADJUSTMENTS", h2)]
story += [P("Your filter is best adjusted by ear to match the prevailing conditions. Because of its numerous "
            "adjustments, you’ll find that if it can’t pull the signal out, nothing can. However, a "
            "few hours practice will be needed to learn its operation. The following table will aid you:")]

rows = [
    ("Desired CW Signal",
     "Peak. Adjust selectivity near full Clockwise (CW). Peak desired station using frequency control. Use "
     "as much selectivity rotation as required for conditions. Note that maximum selectivity produces the "
     "highest gain at the peak."),
    ("SSB, AM, CB, FM, or broadcast station. No hetrodyne or whistle.",
     "Lowpass. Rotate selectivity <b>10%</b> CW or as far as possible without producing audible ringing "
     "(not critical). Turn frequency control for desired rejection of high frequencies. Note: greater than "
     "50% rotation makes signals bassy, because important voice frequencies are rejected."),
    ("Hetrodyne, whistle, TV oscillator radiation (buzzing noise), or code station interfering with desired "
     "signal. Also for CB beats.",
     "Notch. Rotate selectivity <b>40%</b> or more. Adjust frequency control to reject undesired signal. "
     "Large selectivity rotations yield the narrowest and shallowest notch; also the hardest to tune. "
     "Therefore, rotate selectivity no more than required to avoid rejecting the desired signal. Note: to "
     "help find the correct rejection frequency, it may help to momentarily switch to peak, peak the "
     "interference, then switch back to notch. The peaked signal is then rejected. A slight frequency "
     "touchup may help since peak and notch frequencies may not track perfectly."),
    ("SSB, AM, CB, FM or broadcast station.",
     "Under some conditions the following may also be useful:<br/>"
     "1. Peak. Selectivity <b>20%</b> to <b>60%</b> rotated. Frequency adjusted for best clarity. Sometimes "
     "very useful.<br/>"
     "2. Notch. Selectivity 0% to <b>30%</b> rotated. Frequency 0% to 20% rotated. Produces an extremely "
     "sharp cutoff of high frequencies. If a hetrodyne appears, you can quickly turn controls as above. "
     "Preferred by many CB and 160, 80, and 40 meter operators for voice reception."),
    ("Weak CW",
     "An AC voltmeter or scope across the speaker or phones is a big aid in peaking an extremely weak signal, "
     "especially if he fades below the noise occasionally. Also, you can pick up 10 db or so in moonbounce "
     "if you use PDI, a pen recorder, and send at 3-4 WPM! See below."),
    ("Strong signal",
     "A “flat” response is obtained in: 1) Lowpass. Selectivity <b>10%</b>. Frequency 0%. "
     "2) Notch. Select. 100% Freq. 0%. 3) Peak. Select. 0%. Freq. 40%."),
]
data = [[P("CONDITION", cellh), P("USEFUL ADJUSTMENTS", cellh)]]
data += [[P(a, cell), P(b, cell)] for a, b in rows]
tbl = Table(data, colWidths=[150, 390], repeatRows=1)
tbl.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.9, INK),
    ("BOX", (0, 0), (-1, -1), 1.4, INK),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ececec")),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]))
story += [tbl, Spacer(1, 8)]
story += [P("<b>Other notes:</b> Full selectivity in peak is obtained only over the normal code reception "
            "range of 250 to 1300 Hz. Use less than <b>80%</b> selectivity at high frequencies. Full "
            "selectivity in lowpass produces an effect similar to peak, but is not recommended because of "
            "reduced rejection of low frequencies. For use at a specific frequency above 1300HZ, align the "
            "filter at the desired frequency for best results. (see below)")]

summary = Table([
    [P("<u><b>MOST-USEFUL SELECTIVITY POSITIONS:</b></u>", cell), ""],
    [P("<b>PEAK:</b>", cell), P("CW: 30-100%<br/>SSB: 10-60%", cell)],
    [P("<b>NOTCH:</b>", cell), P("WHISTLE: 40-90%", cell)],
    [P("<b>LOWPASS:</b>", cell), P("10-20%", cell)],
    [P("This is just a summary. See Section C for details.<br/><br/>Also note that all QF-1 filters made "
       "have virtually the same selectivity range. However, later models have more selectivity "
       "“bandspread.” So less selectivity rotation is required for the same effect, except near "
       "maximum selectivity.", cell), ""],
], colWidths=[80, 220])
summary.setStyle(TableStyle([
    ("SPAN", (0, 0), (1, 0)), ("SPAN", (0, 4), (1, 4)),
    ("BOX", (0, 0), (-1, -1), 1.0, INK),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 4), (-1, 4), 8), ("BOTTOMPADDING", (0, 4), (-1, 4), 8),
]))
notes = [P("<b>Transcriber\u2019s notes</b>", small)]
for n in [
    "Text is transcribed verbatim from the three-page scan, including the original spelling "
    "(\u201chetrodyne\u201d, \u201creceivers\u201d). Percentages that were hand-corrected on the original are "
    "shown in <b>bold</b>.",
    "Section D (\u201cIn Case of Trouble\u201d) and figs. 1 to 3 for the QF-2 are referred to in the text but "
    "were not part of the scanned document.",
    "The response curves were regenerated from filter models matched to the printed graphs; like the "
    "originals they are qualitative.",
    "All drawings are redrawn as vector art with the original designators, values and pin numbers. On the "
    "schematics the dashed outline is the chassis boundary; dots on it mark leads that leave it. The amplifier "
    "board\u2019s two parallel ground runs are drawn as one ground line. C2\u2013C5 are read as .018 \u00b5F "
    "(C3 is partly illegible; note 2 says the four are matched).",
]:
    notes.append(P("\u2022 " + n, small))
pair = Table([[summary, notes]], colWidths=[305, 235])
pair.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                          ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 14)]))
story += [Spacer(1, 6), pair]

text_part = story
curves_part = [PageBreak(), Drawing(page_curves, 700)]
draw_part = [NextPageTemplate("land"), PageBreak(), Drawing(page_hookup, 548), PageBreak(),
             Drawing(page_amp, 548), PageBreak(), Drawing(page_main, 548)]
story = text_part + curves_part + draw_part

doc = BaseDocTemplate(OUT, pagesize=letter, title="QF-1 Filter Instructions (redrawn)",
                      author="Autek", subject="Autek QF Series Audio Filters - instructions, "
                      "response curves, hookup and schematics, redrawn")
pw, ph = letter
port = PageTemplate("port", [Frame(36, 40, pw - 72, ph - 76, id="f")], onPage=footer, pagesize=letter)
lw_, lh_ = landscape(letter)
land = PageTemplate("land", [Frame(30, 34, lw_ - 60, lh_ - 58, id="g", leftPadding=0, rightPadding=0,
                                   topPadding=0, bottomPadding=0)], onPage=footer,
                    pagesize=landscape(letter))
doc.addPageTemplates([port, land])
doc.build(story)
print("built", OUT)
