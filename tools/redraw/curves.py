"""'A few of the infinite number of responses' - five response charts.
Curves are regenerated from simple filter models fitted to the shapes in the
original printed graphs (qualitative, as in the original)."""
import math
from sch import S, FONTB, FONT


def bp4(f, f0, Q):
    x = f / f0 - f0 / f
    return 2 * 10 * math.log10(1 + (Q * x) ** 2)


def notch(f, f0, Q, depth):
    r = f / f0
    num = (1 - r * r) ** 2
    den = (1 - r * r) ** 2 + (r / Q) ** 2
    g = num / den + 10 ** (-depth / 10)
    return -10 * math.log10(g)


def lp(f, fc, n):
    return 10 * math.log10(1 + (f / fc) ** (2 * n))


def chart(d, x0, y0, W, H, fmin, fmax, ticks, curves, cap, labels=()):
    """x0,y0 = top-left of plot box (local units). curves: list of fn(f)->dB."""
    lx = lambda f: x0 + W * math.log(f / fmin) / math.log(fmax / fmin)
    ly = lambda db: y0 + H * min(db, 60) / 60
    T = d.text
    # grid
    for db in (20, 40):
        d.line((x0, ly(db)), (x0 + W, ly(db)), w=0.6)
    for f, lab in ticks:
        if fmin < f < fmax:
            d.line((lx(f), y0), (lx(f), y0 + H), w=0.6)
    d.rect(x0, y0, x0 + W, y0 + H, w=1.1)
    for db in (0, 20, 40, 60):
        T(x0 - 4, ly(db) + 3, str(db), 7.5, "r", FONTB)
        d.line((x0 - 2, ly(db)), (x0, ly(db)), w=0.8)
    T(x0 - 20, y0 + H * 0.38, "DB", 7.5, "r", FONTB)
    for f, lab in ticks:
        T(lx(f), y0 + H + 10, lab, 7.5, "c", FONTB)
    # curves (clipped to the box)
    N = 400
    for fn in curves:
        seg = []
        for i in range(N + 1):
            f = fmin * (fmax / fmin) ** (i / N)
            db = fn(f)
            if db <= 60.5:
                seg.append((lx(f), ly(max(db, 0))))
            else:
                if len(seg) > 1:
                    seg.append((lx(f), ly(60)))
                    d.line(*seg, w=1.6)
                seg = []
                last_out = True
        if len(seg) > 1:
            d.line(*seg, w=1.6)
    for (fx, dby, text, tx, ty) in labels:
        d.line((lx(fx), ly(dby)), (tx, ty), w=0.7)
        T(tx + 2, ty + 3, text, 7, "l", FONTB)
    T(x0 + 18, y0 + H + 22, cap, 7.5, "l", FONTB)
    return lx, ly


def draw_curves(c, ox, oy, s):
    d = S(c, ox, oy, s)
    T = d.text
    W, H = 190, 120
    T(250, 18, "A FEW OF THE INFINITE\nNUMBER OF RESPONSES", 15, "c", "LSerifB")
    t1 = [(0.2, ".2"), (0.5, ".5"), (1, "1"), (2, "2"), (4, "4")]

    # 1. Peak vs freq, selectivity 100%
    chart(d, 40, 70, W, H, 0.2, 4, t1,
          [lambda f, f0=f0: bp4(f, f0, 14) for f0 in (0.22, 0.5, 1.0, 1.55, 2.2)],
          "PEAK VS. FREQ. (KHZ)\nSELEC. = 100 %")

    # 2. Notch vs freq, selectivity 80%
    chart(d, 300, 70, W, H, 0.2, 4, t1,
          [lambda f, f0=f0, dp=dp: notch(f, f0, 0.7, dp)
           for f0, dp in ((0.25, 43), (0.5, 45), (1.0, 50), (2.0, 75), (3.6, 45))],
          "NOTCH VS. FREQ.\nSELEC. = 80 %")

    # 3. Peak vs selectivity, F = 500 Hz
    t3 = [(0.1, ".1"), (0.25, ".25"), (0.5, ".5"), (1, "1"), (2, "2")]
    qs = (0.22, 0.45, 0.75, 3.2, 7.5)
    lx, ly = chart(d, 40, 250, W, H, 0.1, 2, t3,
                   [lambda f, q=q: bp4(f, 0.5, q) + (lp(f, 2.2, 2) if q < 0.3 else 0) for q in qs],
                   "PEAK VS. SELECTIVITY (F = 500 HZ)",
                   labels=[(1.75, bp4(1.75, 0.5, 0.22) + lp(1.75, 2.2, 2), "0%", 40 + W - 22, 250 + 14),
                           (1.6, bp4(1.6, 0.5, 0.75), "80%", 40 + W - 18, 250 + 50),
                           (1.15, bp4(1.15, 0.5, 3.2), "90%", 40 + W - 16, 250 + 84),
                           (0.8, bp4(0.8, 0.5, 7.5), "100%", 40 + W - 66, 250 + 98)])

    # 4. Notch vs selectivity, F = 1 kHz
    sets = ((0.7, 75), (1.5, 48), (4.0, 22))
    fn4 = [lambda f, q=q, dp=dp: notch(f, 1.0, q, dp) + lp(f, 2.6, 4) for q, dp in sets]
    chart(d, 300, 250, W, H, 0.2, 4, t1, fn4,
          "NOTCH VS. SELEC. (F = 1 KHZ)",
          labels=[(1.08, fn4[2](1.08), "100%", 300 + 152, 250 + 22),
                  (1.0, 48, "80%", 300 + 162, 250 + 62),
                  (1.0, 58, "0%", 300 + 140, 250 + 112)])

    # 5. Lowpass vs freq, selectivity 0-30%
    chart(d, 170, 430, W, H, 0.2, 4, t1,
          [lambda f, fc=fc, n=n: lp(f, fc, n)
           for fc, n in ((0.33, 4), (0.7, 6.6), (0.95, 7.8), (1.3, 9.4), (2.5, 14.7))],
          "LOWPASS VS. FREQ.\nSELEC. = 0–30 %")
