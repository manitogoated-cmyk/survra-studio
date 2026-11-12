import json
# (segment, weight, kind, action, camera text, cam [start, end] as (zoom, fx, fy, rot), shake, transition-in, sfx [(name, frac)], hud_day, prm)
C = lambda z, fx, fy, r=0: [z, fx, fy, r]
S = [
 ('hook', 0.9, 'eyes_open', 'Extreme close-up: his eyes snap open, wet with sea spray', 'ECU, fast push-in', [C(1.15,540,900), C(1.45,540,860)], 0, 'cut', [('impact',0.15),('gasp',0.18)], None, {}),
 ('hook', 1.2, 'overhead_ocean', 'Overhead: one tiny boat alone on an endless ocean', 'Overhead, snap zoom out', [C(3.0,540,1000), C(1.0,540,960)], 0, 'zoom', [('whoosh',0.0),('boom',0.1)], None, {}),
 ('hook', 1.0, 'map_route', 'The drift line races across the Pacific', 'Graphic, push-in', [C(1.0,540,1080), C(1.2,540,1080)], 0, 'whip', [('whoosh',0.0),('riser',0.2)], None, {'p0':0.0,'p1':1.0}),
 ('hook', 1.3, 'beach_crawl', 'He crawls out of the surf and punches the air', 'Low angle tracking', [C(1.3,420,1250), C(1.1,560,1200)], 0, 'flash', [('wave',0.0),('hit',0.75)], None, {}),
 ('depart', 1.2, 'harbour', 'Sunny Mexican harbour; the boat pulls away, gulls overhead', 'Wide tracking shot', [C(1.0,600,960), C(1.15,380,1000)], 0, 'whip', [('gulls',0.0),('whoosh',0.0)], 1, {}),
 ('depart', 1.2, 'pull_cord', 'José yanks the starter cord twice; the engine roars to life', 'Medium side shot, punch-in on start', [C(1.1,540,1050), C(1.3,560,1000)], 0, 'cut', [('cord',0.0),('cord',0.45),('engine_start',0.7)], 1, {}),
 ('depart', 1.1, 'boat_speed', 'The boat rockets past the camera, spray flying', 'Low angle, whip pan', [C(1.2,540,1150), C(1.0,540,1100,-4)], 0, 'cut', [('whoosh',0.3),('splash',0.5)], 1, {}),
 ('depart', 1.3, 'stopwatch', 'A stopwatch spins: a 30-hour trip', 'Graphic punch-in', [C(1.3,540,800), C(1.0,540,800)], 0, 'zoom', [('tick',0.0),('boom',0.55)], None, {}),
 ('storm', 0.8, 'storm_sky', 'Black clouds roll in; lightning cracks', 'Low angle up at the sky', [C(1.1,540,700,-6), C(1.2,540,700,6)], 8, 'flash', [('thunder',0.3)], 2, {}),
 ('storm', 1.0, 'engine_die', 'The engine shakes, sparks and dies; ENGINE DEAD', 'Close-up on the motor', [C(1.0,540,900), C(1.25,540,820)], 10, 'cut', [('sputter',0.0),('clunk',0.8)], 2, {}),
 ('storm', 0.9, 'face_fear', 'José in the rain, eyes darting back toward shore', 'ECU, Dutch tilt', [C(1.1,540,950,-5), C(1.3,560,920,4)], 6, 'cut', [('rain',0.0),('thunder',0.6)], None, {}),
 ('storm', 1.2, 'big_wave', 'A huge wave lifts the boat; both men brace', 'Wide, heavy shake', [C(1.15,540,1000,-8), C(1.0,540,900,8)], 16, 'whip', [('crash',0.4)], 2, {}),
 ('food', 0.8, 'grab_fish', 'A fish leaps; José snatches it bare-handed', 'Close-up at the water surface', [C(1.1,600,1000), C(1.3,560,950)], 0, 'whip', [('splash',0.0),('grab',0.45)], 40, {}),
 ('food', 0.8, 'underwater_turtle', 'Below the hull a turtle swims up toward the boat', 'Underwater, looking up', [C(1.2,540,1100), C(1.0,540,960)], 0, 'zoom', [('bubbles',0.0)], 40, {}),
 ('food', 0.8, 'bird_land', 'A seabird lands on the rail; his hand shoots out', 'Medium, snap zoom on grab', [C(1.0,540,1050), C(1.35,700,1050)], 0, 'cut', [('caw',0.1),('flap',0.4),('grab',0.8)], 40, {}),
 ('food', 0.8, 'rain_drink', 'Face to the sky, he drinks the rain; the bucket fills', 'Medium low angle', [C(1.2,600,1150), C(1.0,600,1100)], 0, 'cut', [('rain',0.0)], 40, {}),
 ('loss', 0.8, 'calendar_flip', 'Calendar pages tear away: MONTH 4', 'Graphic, push-in', [C(1.0,540,800), C(1.2,540,800)], 0, 'flash', [('flip',0.0),('flip',0.25),('flip',0.5),('boom',0.8)], None, {}),
 ('loss', 1.1, 'refuse_food', 'José offers a fish; Ezequiel turns his head away', 'Two-shot, slow push', [C(1.0,540,1150), C(1.2,600,1130)], 0, 'cut', [('heartbeat',0.2)], 120, {}),
 ('loss', 1.1, 'alone_night', 'Night. One man left in the boat under the moon', 'Wide, pull back', [C(2.0,540,1080), C(1.0,540,1000)], 0, 'cut', [('heartbeat',0.0),('low',0.0)], 120, {}),
 ('loss', 1.0, 'face_grief', 'Close on José; a tear runs down', 'ECU, slow push-in', [C(1.05,540,960), C(1.25,540,920)], 0, 'cut', [('heartbeat',0.1)], None, {}),
 ('alone', 1.0, 'ship_pov', 'POV: his arms wave at a ship on the horizon', 'POV from the boat', [C(1.0,540,1000), C(1.15,640,950)], 4, 'whip', [('horn',0.1),('shout',0.3)], 300, {}),
 ('alone', 0.8, 'ship_gone', 'The ship sails on; his arms drop', 'Wide side shot', [C(1.1,500,1000), C(1.0,540,1000)], 0, 'cut', [('horn_far',0.0)], 300, {}),
 ('alone', 1.0, 'tally', 'A knife scratches tally marks on the hull, faster and faster', 'Extreme close-up, tracking the knife', [C(1.2,400,500), C(1.0,540,700)], 0, 'cut', [('scratch',0.05),('scratch',0.3),('scratch',0.55),('scratch',0.8)], None, {'n0':5,'n1':60}),
 ('alone', 1.0, 'moon_montage', 'Moon phases race by; days and nights flicker', 'Wide time-lapse', [C(1.0,540,900), C(1.15,540,850)], 0, 'zoom', [('tick',0.0),('riser',0.5)], 400, {}),
 ('land', 0.9, 'day438', 'Day 438. He lifts his head toward the sunrise', 'Medium, push-in', [C(1.0,540,1050), C(1.35,500,980)], 0, 'flash', [('boom',0.0)], 438, {}),
 ('land', 0.8, 'birds_flyby', 'Birds sweep right past the camera', 'Wide, birds fill frame', [C(1.0,540,960), C(1.1,540,960)], 0, 'whip', [('caw',0.1),('flap',0.3)], 438, {}),
 ('land', 0.8, 'coconut', 'A coconut bobs into frame: land is close', 'Close-up at waterline', [C(1.1,540,800), C(1.3,540,780)], 0, 'cut', [('bloop',0.4)], 438, {}),
 ('land', 1.2, 'island_reveal', 'Over his shoulder, an island rises; he punches the air', 'Over-the-shoulder, crane up', [C(1.3,540,1300), C(1.0,540,1000)], 0, 'cut', [('riser',0.0),('hit',0.7)], 438, {}),
 ('land', 1.1, 'swim', 'He dives in and swims for the shore', 'Half-underwater side tracking', [C(1.1,400,1100), C(1.1,700,1100)], 0, 'whip', [('splash',0.25),('swim',0.4),('swim',0.7)], 438, {}),
 ('land', 1.3, 'map_route', 'The route completes: 6,700 miles', 'Graphic, push-in', [C(1.0,540,1080), C(1.2,540,1080)], 0, 'zoom', [('whoosh',0.0),('boom',0.6)], None, {'p0':0.85,'p1':1.0}),
 ('end', 1.0, 'beach_end', 'Overhead: he lies on the sand as the surf washes in', 'Overhead, slow pull-up', [C(1.4,560,960), C(1.0,540,960)], 0, 'flash', [('wave',0.0),('hit',0.05)], None, {}),
]
out = {'id': 'short-001-alvarenga', 'shots': []}
for i, (seg, w, kind, act, camtxt, cam, shake, tr, sfx, day, prm) in enumerate(S):
    out['shots'].append({'n': i + 1, 'segment': seg, 'weight': w, 'kind': kind, 'action': act, 'camera': camtxt, 'cam': cam,
                         'shake': shake, 'transition': tr, 'sfx': sfx, 'hud_day': day, 'prm': prm})
json.dump(out, open('/home/claude/studio/pilot/storyboard.json', 'w'), indent=1)
print(len(S), 'shots')
