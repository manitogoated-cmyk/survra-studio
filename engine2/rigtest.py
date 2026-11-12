import skia, math
from common import *
import rig
surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(C('#7fb6e0'))
names = ['stand','panic','pull_a','pull_b','grab_b','offer','turn_away','wave_b','drop','scratch_a','drink','swim_a','crawl_a','collapse','fist','dive']
exprs = ['neutral','fear','determined','happy','shock','sad','sad','fear','sad','determined','relief','determined','exhausted','exhausted','relief','determined']
for i,(n,e) in enumerate(zip(names, exprs)):
    x = 140 + (i%4)*260; y = 380 + (i//4)*420
    rig.draw_person(cv, x, y, 0.75, rig.pose(n), rig.EZEQ if n in ('turn_away',) else rig.JOSE, e, 1.0)
    cv.drawString(n, x-80, y+90, skia.Font(TF_BOLD, 28), P(C('#000000')))
surf.makeImageSnapshot().save('/home/claude/studio/pilot/rig_sheet.png', skia.kPNG)
s2 = skia.Surface(W, H); c2 = s2.getCanvas(); c2.clear(C('#1b2a3a'))
for i,e in enumerate(['fear','sad','relief','determined']):
    rig.draw_face_closeup(c2, 270 + (i%2)*540, 480 + (i//2)*960, 0.55, rig.JOSE, e, 1.0, look=(0.3,-0.2), wet=(e=='fear'), tear=0.5 if e=='sad' else 0)
s2.makeImageSnapshot().save('/home/claude/studio/pilot/face_sheet.png', skia.kPNG)
