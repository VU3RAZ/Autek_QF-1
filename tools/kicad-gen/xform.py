def xform(px, py, rot=0, mirror=None):
    """library pin offset (y up) -> sheet offset (y down)"""
    if mirror == "x":
        py = -py
    elif mirror == "y":
        px = -px
    x, y = px, -py            # to screen coords
    for _ in range((rot // 90) % 4):   # CCW visual rotation
        x, y = y, -x
    return x, y
