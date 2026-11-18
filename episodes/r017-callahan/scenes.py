"""Case 017 - Steven Callahan, 76 days adrift in an inflatable raft in 1982.
The whole story is filmed in 3D (world3d.py). This file holds only the 2D overlays drawn on top of 3D shots (spray on
the night sea, motes in the water, glare under the sun, stars, the sign-off). No flat inserts."""
import math

from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
ORANGE, AMBER = h('FF7A1A'), h('FFB000')


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x99C8DCF0, 81, size=(2, 6), drift=(-220, 90), wobble=30, twinkle=False)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0x77D8F4FF, 83, size=(2, 6), drift=(10, -40), wobble=30, twinkle=True)


def glare(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x55FFF8E0, 85, size=(3, 8), drift=(16, -12), wobble=20, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 14, 0x66FFFFFF, 87, size=(2, 4), drift=(-12, 4), wobble=8, twinkle=True)


def closed(cv, c):
    if c.lt > 0.3:
        k = min(1, (c.lt - 0.3) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 017', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}
OVER = dict(cabin_flood=spray, boat_sink=spray, raft_jump=spray, raft_alone=spray, rook_raft=spray, still_close=glare, rook_still=glare,
            under_fish=motes, fish_catch=motes, spear_hole=motes, fish_hull=motes, patch_fail=glare, fork_fix=glare, thin_man=glare,
            night_lights=stars, rook_lights=stars, signoff=closed)
