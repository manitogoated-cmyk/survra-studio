"""Case 044 - children by parcel post, 1913 to 1915. The story is filmed in 3D (world3d.py); this file holds only the 2D
overlays drawn on top of the 3D shots (dust in the lamplight, snow in the air, soot and the sign-off). There are no flat
inserts in this Short. Every overlay is drawn by this code; nothing reproduces a real photograph, stamp, logo or document."""
from engine3 import world as Wd

W, H = 1080, 1920
AMBER = Wd.hexc('FFB000')


def motes(cv, c):
    """Indoors: dust turning slowly in the window light."""
    Wd.particles(cv, W, H, c.t, 16, 0x55FFE8C0, 71, size=(1.5, 4), drift=(12, -9), wobble=18, twinkle=True)


def snow(cv, c):
    """Out of doors in February: a little snow on the wind."""
    Wd.particles(cv, W, H, c.t, 26, 0x99FFFFFF, 73, size=(2, 5), drift=(-60, 90), wobble=30)


def soot(cv, c):
    """Inside the mail car: cinders and dust shaken loose."""
    Wd.particles(cv, W, H, c.t, 14, 0x66FFC890, 75, size=(1.5, 4), drift=(-40, 12), wobble=22, twinkle=True)


def dusk(cv, c):
    """The Ohio lane at dusk: a few slow flakes."""
    Wd.particles(cv, W, H, c.t, 14, 0x77FFE0C0, 77, size=(2, 4), drift=(-20, 50), wobble=24)


def closed(cv, c):
    motes(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 360)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 044', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}

OVER = dict(scale_girl=motes, dial=motes, stamp_on=motes, rook_counter=motes, parents=motes, coat_close=motes, rook_ticket=motes,
            rook_scale=motes, weigh_wide=motes, limit=motes, train_wide=snow, wheels=snow, car_inside=soot, rook_sack=soot,
            rook_sackcheck=soot, cousin=soot, car_window=soot, baby_bundle=dusk, rook_hatjump=dusk, carrier_lane=dusk, rook_follow=dusk,
            ohio_door=dusk, door=snow, rook_delivered=snow, ban_desk=motes, rook_notice=motes, anyway_counter=motes, rook_laugh=motes,
            signoff=closed)
