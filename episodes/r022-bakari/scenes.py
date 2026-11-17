"""Case 022 - placeholder inserts (draft)."""
from engine3 import world as Wd

W, H = 1080, 1920


def _card(cv, c):
    Wd.vgrad(cv, 0, 0, W, H, [(0, Wd.hexc('10283A')), (1, Wd.hexc('060C14'))])


def fell_card(cv, c):
    _card(cv, c)


def landed_card(cv, c):
    _card(cv, c)


def board(cv, c):
    _card(cv, c)


SHOTS = dict(fell_card=fell_card, landed_card=landed_card, board=board)
OVER = {}
