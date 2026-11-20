import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import fonts
fonts.register()

which = sys.argv[1]
c = canvas.Canvas(f"/tmp/t_{which}.pdf", pagesize=landscape(letter))
if which == "amp":
    from amp import draw_amp, draw_amp_layout
    draw_amp(c, 50, 560, 0.85)
    draw_amp_layout(c, 60, 170, 1.0)
elif which == "main":
    from mainboard import draw_main
    draw_main(c, 40, 585, 0.68)
elif which == "hook":
    from hookup import draw_hookup
    draw_hookup(c, 30, 580, 0.72)
elif which == "curves":
    from curves import draw_curves
    draw_curves(c, 120, 590, 1.0)
c.showPage()
c.save()
