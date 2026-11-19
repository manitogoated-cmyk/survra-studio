"""Case 041 - the exploding whale of Florence, Oregon, 12 November 1970. The story is filmed in 3D (world3d.py); this
file holds only the 2D overlays drawn on top of the 3D shots (blown sand, flying specks of blubber, sea spray, the
sign-off). There are no flat inserts in this Short. Every overlay is drawn by this code; nothing reproduces a real
photograph, film frame, logo or document."""
import math

from concepts.chars import P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
AMBER = h('FFB000')


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def grit(cv, c):
    """Blown sand and specks of blubber drifting down past the lens after the blast."""
    Wd.particles(cv, W, H, c.t, 30, 0xAAE0CCA0, 41, size=(2, 6), drift=(40, 260), wobble=30)
    Wd.particles(cv, W, H, c.t, 12, 0x99D8CABE, 43, size=(4, 9), drift=(-30, 340), wobble=40)


def blast(cv, c):
    """The first instants of the blast: a hot white bloom over the frame that fades in a third of a second, then grit."""
    if c.prm.get('loop'):
        breeze(cv, c)
        return
    u = c.lt - 0.22
    if 0 < u < 0.35:
        a = (1 - u / 0.35) ** 2
        Wd.glow(cv, 540, 900, 900, h('FFF2D0'), a=0.75 * a)
    if u > 0:
        grit(cv, c)


def streaks(cv, c):
    """Lumps whistling past: short speed lines across the sky."""
    for i in range(14):
        x = (W * rn(i, 5) + c.t * (900 + 500 * rn(i, 6))) % (W + 400) - 200
        y = H * 0.08 + H * 0.45 * rn(i, 7)
        cv.drawLine(x, y, x - 120 - 80 * rn(i, 8), y - 30, P(h('FFFFFF'), 3, a=0.22))
    grit(cv, c)


def breeze(cv, c):
    """Sea air: a few grains of sand on the wind."""
    Wd.particles(cv, W, H, c.t, 16, 0x66F2E6C8, 47, size=(1.5, 4), drift=(90, 14), wobble=14, twinkle=True)


def pollen(cv, c):
    Wd.particles(cv, W, H, c.t, 18, 0x66FFF2C8, 49, size=(2, 4), drift=(16, -20), wobble=18, twinkle=True)


def closed(cv, c):
    breeze(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 360)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 041', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}

OVER = dict(blast_close=blast, column=grit, chunk_lens=streaks, rain_crowd=grit, rook_dune=grit, overhead_chunk=streaks, run_cars=grit,
            rook_duck=grit, crates=breeze, rook_count=breeze, gull=breeze, wire=breeze, expert=breeze, warn_talk=breeze,
            walk_back=breeze, rook_eye=breeze, slab_fall=streaks, car_crush=grit, owner_face=grit, rook_roof=breeze,
            showroom=pollen, rook_laugh=breeze, bulldozer=grit, rook_nose=grit, engineer_turn=breeze, engineer=breeze,
            rook_stare=breeze, rook_park=pollen, park_sign=pollen, signoff=closed)
