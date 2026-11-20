from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

L = "/usr/share/fonts/truetype/liberation/"


def register():
    pdfmetrics.registerFont(TTFont("LSans", L + "LiberationSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("LSansB", L + "LiberationSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("LSansI", L + "LiberationSans-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("LSerif", L + "LiberationSerif-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("LSerifB", L + "LiberationSerif-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("LSerifI", L + "LiberationSerif-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("LSerifBI", L + "LiberationSerif-BoldItalic.ttf"))
    addMapping("LSerif", 0, 0, "LSerif")
    addMapping("LSerif", 1, 0, "LSerifB")
    addMapping("LSerif", 0, 1, "LSerifI")
    addMapping("LSerif", 1, 1, "LSerifBI")
    addMapping("LSans", 0, 0, "LSans")
    addMapping("LSans", 1, 0, "LSansB")
    addMapping("LSans", 0, 1, "LSansI")
    addMapping("LSans", 1, 1, "LSansB")
