"""Case 043 - the Captain of Koepenick, 1906. The story is filmed in 3D (world3d.py); this file holds only the 2D
overlays drawn on top of the 3D shots (dust in window light, street grit, gaslight flecks, footlight sparkle and the
sign-off). There are no flat inserts in this Short. Every overlay is drawn by this code; nothing reproduces a real
photograph, film frame, logo or document."""
from engine3 import world as Wd

W, H = 1080, 1920
AMBER = Wd.hexc('FFB000')


def motes(cv, c):
    """Indoors: dust turning slowly in the lamplight."""
    Wd.particles(cv, W, H, c.t, 16, 0x55FFE8C0, 61, size=(1.5, 4), drift=(14, -10), wobble=18, twinkle=True)


def grit(cv, c):
    """Out of doors: street dust blowing low across the cobbles."""
    Wd.particles(cv, W, H, c.t, 14, 0x66D8CCB8, 63, size=(2, 5), drift=(70, 24), wobble=26)


def gas(cv, c):
    """The alley and the cell: a few warm flecks under the lamp."""
    Wd.particles(cv, W, H, c.t, 12, 0x66FFB868, 65, size=(1.5, 4), drift=(-10, -22), wobble=20, twinkle=True)


def limelight(cv, c):
    """The theatre: bright dust in the spotlight."""
    Wd.particles(cv, W, H, c.t, 22, 0x77FFF0D0, 67, size=(1.5, 5), drift=(8, -26), wobble=24, twinkle=True)


def closed(cv, c):
    limelight(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 360)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 043', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


SHOTS = {}

OVER = dict(office_burst=motes, boots_in=motes, captain_point=motes, mayor_up=motes, rook_desk=motes, treasurer=motes, cash=motes,
            rook_coins=motes, line_up=grit, mayor_march=grit, rook_peer=grit, walk_out=grit, rook_gone=grit, cap_off=gas, cobbler=motes,
            rook_shoe=motes, shop=motes, rook_mag=motes, dress=motes, halt=grit, rook_follow=grit, caught=gas, rook_cell=gas, kaiser=motes,
            rook_free=gas, stage=limelight, rook_seat=limelight, rook_wings=limelight, signoff=closed)
