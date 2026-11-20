"""Case 042 - the Idaho beaver drop, 1948. The story is filmed in 3D (world3d.py); this file holds only the 2D overlays
drawn on top of the 3D shots (wind streaks in the air, drifting seeds in the meadow, wood chips, spray, the sign-off).
There are no flat inserts in this Short. Every overlay is drawn by this code; nothing reproduces a real photograph,
film frame, logo or document."""
import math

from concepts.chars import P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
AMBER = h('FFB000')


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def air(cv, c):
    """Falling through the air: thin wind streaks rushing up past the lens."""
    for i in range(12):
        x = W * rn(i, 5)
        y = (H * rn(i, 6) - c.t * (1400 + 600 * rn(i, 7))) % (H + 300) - 150
        cv.drawLine(x, y, x + 8, y + 140 + 90 * rn(i, 8), P(h('FFFFFF'), 2, a=0.18))


def seeds(cv, c):
    """Meadow air: a few seeds and midges drifting in the sun."""
    Wd.particles(cv, W, H, c.t, 16, 0x66FFF2C8, 51, size=(1.5, 4), drift=(30, -12), wobble=16, twinkle=True)


def chips(cv, c):
    Wd.particles(cv, W, H, c.t, 10, 0x88E8CFA0, 53, size=(2, 5), drift=(60, 180), wobble=30)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 14, 0x77E6F2F6, 55, size=(2, 5), drift=(-20, 120), wobble=24)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 18, 0x88C8B48A, 57, size=(2, 6), drift=(50, 90), wobble=30)


def wind(cv, c):
    """The open cargo door: streaks flying sideways past the lens."""
    for i in range(14):
        y = H * 0.1 + H * 0.55 * rn(i, 9)
        x = (W * rn(i, 10) - c.t * (1600 + 700 * rn(i, 11))) % (W + 400) - 200
        cv.drawLine(x, y, x + 160 + 100 * rn(i, 12), y + 6, P(h('FFFFFF'), 2, a=0.16))


def closed(cv, c):
    seeds(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 360)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 042', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}

OVER = dict(drop_close=air, drop_wide=air, hole_close=air, rook_box_ride=air, meadow_land=dust, box_open=seeds, rook_land=dust,
            town_tree=chips, town_flood=seeds, rook_flood=spray, mule_load=dust, mule_buck=dust, rook_mule=dust,
            chute_crate=seeds, rook_test=seeds, test_drop=seeds, geronimo_out=dust, rook_tally=seeds, geronimo_back=seeds,
            rook_jaw=seeds, rook_heter=seeds, hold=wind, rook_hold=wind, plane_wide=air, rook_hush=seeds, dam_wide=spray,
            lodge=spray, rook_dam=seeds, signoff=closed)
