"""Case 023 - Annette Herfkens, eight days beside the wreck of Vietnam Airlines Flight 474, 1992.
The whole story is filmed in 3D (world3d.py). This file holds only the 2D overlays drawn on top of 3D shots (rain on
the slope, sun motes, mist at dawn, the sign-off). No flat inserts."""
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
AMBER = h('FFB000')


def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=130, c=0x66CFE6FF, slant=0.22, speed=2100, length=58)


def storm(cv, c):
    Wd.rain(cv, W, H, c.t, density=170, c=0x77CFE6FF, slant=0.35, speed=2600, length=70)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=60, c=0x44CFE6FF, slant=0.15, speed=1700, length=40)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x55FFF4D0, 231, size=(2, 6), drift=(12, -16), wobble=20, twinkle=True)


def mist(cv, c):
    Wd.particles(cv, W, H, c.t, 18, 0x44FFF0D8, 233, size=(3, 7), drift=(10, -10), wobble=16, twinkle=True)


def fireflies(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0xCCE8FF90, 235, size=(3, 7), drift=(8, -14), wobble=40, twinkle=True)


def closed(cv, c):
    motes(cv, c)
    if c.lt > 0.3:
        k = min(1, (c.lt - 0.3) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 023', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}
OVER = dict(crash_ridge=storm, wreck_wide=rain, wing_torn=rain, rook_doubt=rain, rook_hatoff=rain, man_beside=drizzle,
            her_alone=rain, thirst_face=motes, wing_pov=motes, rook_squeeze=motes, elbow_crawl=motes, tuft_pull=motes,
            rook_nod=motes, rain_arrives=storm, tuft_drink=rain, officer_trees=mist, officer_ghost=mist, rook_brim=mist,
            carry_down=motes, night_wreck=fireflies, calm_face=fireflies, rook_vigil=fireflies, rook_wreck=motes, carry_light=mist, signoff=closed)
